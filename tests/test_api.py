from fastapi.testclient import TestClient

from api.server import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    assert "potential_score" not in str(body)


def test_analyze_rejects_invalid_cost() -> None:
    response = client.post(
        "/analyze",
        json={"name": "Box", "category": "Storage", "cost": 0, "market": "PH"},
    )

    assert response.status_code == 422
