from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dashboard_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "DisasterGuard Pilot Demo v1" in response.text
    assert "Executive Overview" in response.text
    assert "Priority Queue" in response.text
    assert "Mock Map Priority View" in response.text
    assert "Incident Detail Panel" in response.text
    assert "Data-Source Readiness Panel" in response.text
    assert "GISTDA Hotspot Context" in response.text


def test_static_assets_available():
    js_response = client.get("/static/app.js")
    css_response = client.get("/static/styles.css")
    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "buildPilotDemo" in js_response.text
    assert "readinessByIncidentType" in js_response.text
    assert "loadGistdaContext" in js_response.text
    assert "color-scheme" in css_response.text
    assert "queue-table" in css_response.text
    assert "readiness-list" in css_response.text
    assert "gistda-context-grid" in css_response.text


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "DisasterGuard GISTDA Demo"}


def test_incident_score_endpoint_wildfire():
    payload = {
        "area_id": "NTH-CHIANGMAI-001",
        "incident_type": "wildfire_haze",
        "hazard_score": 0.82,
        "exposure_score": 0.74,
        "urgency_score": 0.79,
        "confidence": 0.76,
        "risk_drivers": ["recent hotspot cluster", "vegetation stress", "low humidity", "wind spread potential", "nearby community exposure"],
    }
    response = client.post("/api/incident/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["area_id"] == "NTH-CHIANGMAI-001"
    assert data["incident_type"] == "wildfire_haze"
    assert data["priority_score"] == 0.78
    assert data["severity"] == "HIGH"
    assert data["recommended_action"] == "PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE"
    assert data["risk_drivers"] == payload["risk_drivers"]


def test_invalid_score_rejected():
    payload = {
        "area_id": "NTH-CHIANGMAI-001",
        "incident_type": "wildfire_haze",
        "hazard_score": 1.2,
        "exposure_score": 0.74,
        "urgency_score": 0.79,
        "confidence": 0.76,
        "risk_drivers": [],
    }
    response = client.post("/api/incident/score", json=payload)
    assert response.status_code == 422


def test_invalid_incident_type_rejected():
    payload = {
        "area_id": "NTH-CHIANGMAI-001",
        "incident_type": "earthquake",
        "hazard_score": 0.82,
        "exposure_score": 0.74,
        "urgency_score": 0.79,
        "confidence": 0.76,
        "risk_drivers": [],
    }
    response = client.post("/api/incident/score", json=payload)
    assert response.status_code == 422
