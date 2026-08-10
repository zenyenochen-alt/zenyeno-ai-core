"""FastAPI entry point with history, access control, and a browser demo."""

from __future__ import annotations

import logging
import os
import re
import secrets
import time
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock
from uuid import uuid4

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from core.agent_controller import AgentController
from core.automation_bridge import build_candidate_import, import_candidate
from core.models import AnalysisHistory, AnalysisRecord, ProductAnalysis, ProductInput
from database.product_db import AnalysisRepository

logger = logging.getLogger("zenyeno.api")
logger.setLevel(logging.INFO)
load_dotenv()


class SlidingWindowRateLimiter:
    def __init__(self, requests_per_minute: int) -> None:
        self.limit = requests_per_minute
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        cutoff = now - 60
        with self._lock:
            timestamps = self._requests[key]
            while timestamps and timestamps[0] < cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return False
            timestamps.append(now)
            return True


def create_app(database_path: str | None = None) -> FastAPI:
    resolved_database_path = database_path or os.getenv("DATABASE_PATH", "data/analyses.db")
    configured_api_key = os.getenv("ZENYENO_API_KEY")
    automation_api_url = os.getenv("AUTOMATION_API_URL", "").strip()
    automation_api_key = os.getenv("AUTOMATION_API_KEY", "").strip()
    persistence_enabled = bool(configured_api_key) or os.getenv(
        "PERSIST_ANALYSES", "false"
    ).lower() in {"1", "true", "yes"}
    repository = AnalysisRepository(
        resolved_database_path if persistence_enabled else ":memory:"
    )
    try:
        requests_per_minute = max(1, int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")))
    except ValueError as error:
        raise RuntimeError("RATE_LIMIT_PER_MINUTE must be an integer") from error
    rate_limiter = SlidingWindowRateLimiter(requests_per_minute)
    controller = AgentController(repository=repository if persistence_enabled else None)

    application = FastAPI(
        title="Zenyeno AI Ecommerce Product Analysis Engine",
        description="Product research, potential scoring, and pricing optimization API.",
        version="1.1.0",
    )

    allowed_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if allowed_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "DELETE"],
            allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
        )

    async def authorize(
        request: Request,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ) -> None:
        if configured_api_key and (
            x_api_key is None or not secrets.compare_digest(x_api_key, configured_api_key)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="A valid X-API-Key header is required.",
            )
        client_host = request.client.host if request.client else "unknown"
        if not rate_limiter.allow(client_host):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )

    async def authorize_history(
        request: Request,
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    ) -> None:
        if not configured_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="History API is disabled until ZENYENO_API_KEY is configured.",
            )
        await authorize(request, x_api_key)

    @application.middleware("http")
    async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
        supplied_request_id = request.headers.get("X-Request-ID", "")
        request_id = (
            supplied_request_id
            if re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", supplied_request_id)
            else str(uuid4())
        )
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed request_id=%s path=%s", request_id, request.url.path)
            raise
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        logger.info(
            "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
        )
        return response

    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def demo() -> HTMLResponse:
        page = Path(__file__).resolve().parent.parent / "web" / "index.html"
        return HTMLResponse(page.read_text(encoding="utf-8"))

    @application.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "version": application.version}

    @application.post(
        "/analyze",
        response_model=ProductAnalysis,
        tags=["analysis"],
        dependencies=[Depends(authorize)],
    )
    def analyze(product: ProductInput) -> ProductAnalysis:
        return controller.analyze(product)

    @application.post(
        "/analyze/import",
        tags=["analysis"],
        dependencies=[Depends(authorize)],
    )
    def analyze_and_import(product: ProductInput) -> dict:
        if not automation_api_url or not automation_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Automation bridge is not configured.",
            )
        analysis = controller.analyze(product)
        payload = build_candidate_import(product, analysis)
        try:
            receipt = import_candidate(automation_api_url, automation_api_key, payload)
        except (httpx.HTTPError, RuntimeError, ValueError) as error:
            logger.exception("candidate_import_failed product=%s", product.name)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="The analysis completed, but the private candidate import failed.",
            ) from error
        return {"analysis": analysis.model_dump(), "import_receipt": receipt}

    @application.get(
        "/analyses",
        response_model=AnalysisHistory,
        tags=["history"],
        dependencies=[Depends(authorize_history)],
    )
    def list_analyses(
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
    ) -> AnalysisHistory:
        return repository.list(limit=limit, offset=offset)

    @application.get(
        "/analyses/{record_id}",
        response_model=AnalysisRecord,
        tags=["history"],
        dependencies=[Depends(authorize_history)],
    )
    def get_analysis(record_id: int) -> AnalysisRecord:
        record = repository.get(record_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Analysis record not found.")
        return record

    @application.delete(
        "/analyses/{record_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["history"],
        dependencies=[Depends(authorize_history)],
    )
    def delete_analysis(record_id: int) -> None:
        if not repository.delete(record_id):
            raise HTTPException(status_code=404, detail="Analysis record not found.")

    return application


app = create_app()
