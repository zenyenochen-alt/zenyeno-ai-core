from fastapi.testclient import TestClient

from api.server import create_app


client = TestClient(create_app(":memory:"))


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "1.1.0"}
    assert response.headers["X-Request-ID"]


def test_demo_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Zenyeno Intelligence Engine" in response.text


def test_analyze_endpoint() -> None:
    response = client.post(
        "/analyze",
        json={
            "name": "Foldable Storage Box",
            "category": "Home Storage",
            "cost": 5,
            "market": "TikTok Philippines",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["final_score"] == 85
    assert body["prediction"]["final_score"] == 85
    assert body["pricing"]["total_cost"] == 5
    assert "potential_score" not in str(body)


def test_analyze_rejects_invalid_cost() -> None:
    response = client.post(
        "/analyze",
        json={"name": "Box", "category": "Storage", "cost": 0, "market": "PH"},
    )

    assert response.status_code == 422


def test_analyze_rejects_impossible_revenue_allocation() -> None:
    response = client.post(
        "/analyze",
        json={
            "name": "Box",
            "category": "Storage",
            "cost": 5,
            "market": "PH",
            "platform_fee_percent": 30,
            "tax_percent": 20,
            "return_rate_percent": 20,
            "target_margin_percent": 30,
        },
    )

    assert response.status_code == 422


def test_api_key_protection(monkeypatch) -> None:
    monkeypatch.setenv("ZENYENO_API_KEY", "test-secret")
    protected_client = TestClient(create_app(":memory:"))

    denied = protected_client.post(
        "/analyze",
        json={"name": "Box", "category": "Storage", "cost": 5, "market": "PH"},
    )
    allowed = protected_client.post(
        "/analyze",
        headers={"X-API-Key": "test-secret"},
        json={"name": "Box", "category": "Storage", "cost": 5, "market": "PH"},
    )

    assert denied.status_code == 401
    assert allowed.status_code == 200

    history = protected_client.get("/analyses", headers={"X-API-Key": "test-secret"})
    assert history.status_code == 200
    assert history.json()["total"] == 1
    record_id = history.json()["items"][0]["id"]

    detail = protected_client.get(
        f"/analyses/{record_id}", headers={"X-API-Key": "test-secret"}
    )
    assert detail.status_code == 200
    assert detail.json()["result"]["product"] == "Box"

    deleted = protected_client.delete(
        f"/analyses/{record_id}", headers={"X-API-Key": "test-secret"}
    )
    assert deleted.status_code == 204


def test_history_is_private_without_configured_api_key() -> None:
    response = client.get("/analyses")

    assert response.status_code == 503


def test_rate_limit(monkeypatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")
    limited_client = TestClient(create_app(":memory:"))
    payload = {"name": "Box", "category": "Storage", "cost": 5, "market": "PH"}

    assert limited_client.post("/analyze", json=payload).status_code == 200
    assert limited_client.post("/analyze", json=payload).status_code == 200
    assert limited_client.post("/analyze", json=payload).status_code == 429


def test_multiple_products_are_not_hardcoded() -> None:
    products = [
        {"name": "Kitchen Organizer", "category": "Kitchen", "cost": 3, "market": "TikTok Philippines"},
        {"name": "Pet Toy", "category": "Pet", "cost": 2, "market": "TikTok Thailand"},
        {"name": "LED Lamp", "category": "Home", "cost": 8, "market": "TikTok Malaysia"},
    ]

    results = [client.post("/analyze", json=product).json() for product in products]

    assert [result["product"] for result in results] == [product["name"] for product in products]
    assert len({result["final_score"] for result in results}) > 1
