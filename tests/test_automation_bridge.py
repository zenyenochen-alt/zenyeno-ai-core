import httpx
from fastapi.testclient import TestClient

from api.server import create_app
from core.agent_controller import AgentController
from core.automation_bridge import build_candidate_import, market_region
from core.models import ProductInput


def test_market_region_mapping() -> None:
    assert market_region("TikTok Philippines") == "PH"
    assert market_region("TH") == "TH"


def test_candidate_payload_preserves_analysis_score() -> None:
    product = ProductInput(name="Storage Box", category="Home", cost=5, market="TikTok Philippines")
    analysis = AgentController().analyze(product)
    payload = build_candidate_import(product, analysis)
    candidate = payload["candidates"][0]

    assert payload["source"] == "ZENYENO_ANALYSIS"
    assert candidate["region"] == "PH"
    assert candidate["metrics"]["zenyeno_final_score"] == analysis.final_score
    assert candidate["candidate_id"].startswith("zenyeno-")


def test_analyze_import_requires_private_bridge_configuration(monkeypatch) -> None:
    monkeypatch.delenv("AUTOMATION_API_URL", raising=False)
    monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)
    client = TestClient(create_app(":memory:"))
    response = client.post(
        "/analyze/import",
        json={"name": "Storage Box", "category": "Home", "cost": 5, "market": "PH"},
    )
    assert response.status_code == 503


def test_analyze_import_calls_private_engine(monkeypatch) -> None:
    monkeypatch.setenv("AUTOMATION_API_URL", "https://private.example")
    monkeypatch.setenv("AUTOMATION_API_KEY", "private-secret")

    def fake_post(url, *, headers, json, timeout):
        assert url == "https://private.example/api/internal/candidates/import"
        assert headers == {"Authorization": "Bearer private-secret"}
        assert json["source"] == "ZENYENO_ANALYSIS"
        return httpx.Response(
            200,
            json={"status": "ok", "imported": 1, "candidates": [{"candidate_id": "test"}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr("core.automation_bridge.httpx.post", fake_post)
    client = TestClient(create_app(":memory:"))
    response = client.post(
        "/analyze/import",
        json={"name": "Storage Box", "category": "Home", "cost": 5, "market": "PH"},
    )
    assert response.status_code == 200
    assert response.json()["import_receipt"]["imported"] == 1
