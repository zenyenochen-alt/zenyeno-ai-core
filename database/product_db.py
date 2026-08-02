"""SQLite-backed analysis history.

The repository owns one connection and serializes access so it works with
FastAPI's thread pool. PostgreSQL can replace this adapter without changing the
analysis pipeline or API contracts.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from core.models import AnalysisHistory, AnalysisRecord, ProductAnalysis, ProductInput


class AnalysisRepository:
    def __init__(self, database_path: str = "data/analyses.db") -> None:
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = Lock()
        self._create_schema()

    def _create_schema(self) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )

    def save(self, request: ProductInput, result: ProductAnalysis) -> AnalysisRecord:
        created_at = datetime.now(timezone.utc)
        with self._lock, self._connection:
            cursor = self._connection.execute(
                "INSERT INTO analyses (created_at, request_json, result_json) VALUES (?, ?, ?)",
                (
                    created_at.isoformat(),
                    request.model_dump_json(),
                    result.model_dump_json(),
                ),
            )
            record_id = int(cursor.lastrowid)
        return AnalysisRecord(id=record_id, created_at=created_at, request=request, result=result)

    def get(self, record_id: int) -> AnalysisRecord | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT id, created_at, request_json, result_json FROM analyses WHERE id = ?",
                (record_id,),
            ).fetchone()
        return self._to_record(row) if row else None

    def list(self, limit: int = 20, offset: int = 0) -> AnalysisHistory:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT id, created_at, request_json, result_json
                FROM analyses ORDER BY id DESC LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            total = int(self._connection.execute("SELECT COUNT(*) FROM analyses").fetchone()[0])
        return AnalysisHistory(items=[self._to_record(row) for row in rows], total=total)

    def delete(self, record_id: int) -> bool:
        with self._lock, self._connection:
            cursor = self._connection.execute("DELETE FROM analyses WHERE id = ?", (record_id,))
        return cursor.rowcount > 0

    @staticmethod
    def _to_record(row: sqlite3.Row) -> AnalysisRecord:
        return AnalysisRecord(
            id=int(row["id"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            request=ProductInput.model_validate(json.loads(row["request_json"])),
            result=ProductAnalysis.model_validate(json.loads(row["result_json"])),
        )
