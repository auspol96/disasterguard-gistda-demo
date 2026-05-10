from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "DisasterGuard GISTDA Demo",
    }


def test_score_endpoint():
    response = client.post(
        "/api/incident/score",
        json={
            "area_id": "NTH-CHIANGMAI-001",
            "incident_type": "wildfire_haze",
            "hazard_score": 0.82,
            "exposure_score": 0.74,
            "urgency_score": 0.79,
            "confidence": 0.76,
            "risk_drivers": [
                "recent hotspot cluster",
                "vegetation stress",
                "low humidity",
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["priority_score"] == 0.78
    assert response.json()["severity"] == "HIGH"
    assert response.json()["recommended_action"] == (
        "PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE"
    )


def test_score_endpoint_validates_score_range():
    response = client.post(
        "/api/incident/score",
        json={
            "area_id": "NTH-INVALID-001",
            "incident_type": "wildfire_haze",
            "hazard_score": 1.2,
            "exposure_score": 0.5,
            "urgency_score": 0.5,
            "confidence": 0.5,
            "risk_drivers": [],
        },
    )

    assert response.status_code == 422
