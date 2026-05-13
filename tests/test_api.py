from fastapi.testclient import TestClient
import app.main as main_module
from app.main import app

client = TestClient(app)


def test_dashboard_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "ForestGuard North Thailand" in response.text
    assert "Forest Priority Intelligence for Wildfire, Haze, and Community Protection" in response.text
    assert "Real Connector v1" in response.text
    assert "Refresh Live GISTDA Data" in response.text
    assert "Leaflet map centered on the GISTDA hotspot" in response.text
    assert "Current Hotspot Evidence" in response.text
    assert "Recommended action" in response.text
    assert "Top Forest Priority Areas" in response.text
    assert "Refresh Multi-area Ranking" in response.text


def test_static_assets_available():
    js_response = client.get("/static/app.js")
    css_response = client.get("/static/styles.css")
    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "fetch(\"/api/gistda/hotspot-context\"" in js_response.text
    assert "fetch(\"/api/gistda/refresh-hotspot-context\"" in js_response.text
    assert "fetch(\"/api/incident/score\"" in js_response.text
    assert "refreshDashboard" in js_response.text
    assert "loadDashboard" in js_response.text
    assert "buildScorePayloadFromContext" in js_response.text
    assert "Refreshing..." in js_response.text
    assert "Live GISTDA data refreshed successfully" in js_response.text
    assert "fetch(\"/api/forest-priority/ranking\"" in js_response.text
    assert "fetch(\"/api/forest-priority/refresh-ranking\"" in js_response.text
    assert "refreshRanking" in js_response.text
    assert "renderRanking" in js_response.text
    assert "buildHotspotPopup" in js_response.text
    assert "connectorBadge.hidden = resolvedStatus !== \"ok\"" in js_response.text
    assert "color-scheme" in css_response.text
    assert ".map" in css_response.text
    assert ".metrics-grid" in css_response.text
    assert ".risk-drivers" in css_response.text
    assert ".hotspot-popup" in css_response.text
    assert ".refresh-message" in css_response.text
    assert ".ranking-table" in css_response.text
    assert ".pattern-detail-panel" in css_response.text
    assert ".environment-grid" in css_response.text
    assert "Live Open-Meteo" in js_response.text


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "DisasterGuard GISTDA Demo"}


def test_forest_priority_areas_endpoint():
    response = client.get("/api/forest-priority/areas")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["areas"]) == 5
    assert payload["areas"][0]["area_id"] == "NTH-CHIANGDAO-MUEANGNA-001"
    assert payload["areas"][0]["lat"] == 19.57651
    assert payload["areas"][0]["lon"] == 99.01361


def test_forest_priority_ranking_missing(monkeypatch, tmp_path):
    missing_path = tmp_path / "forest_priority_ranking.json"
    monkeypatch.setattr(main_module, "FOREST_PRIORITY_RANKING_PATH", missing_path)

    response = client.get("/api/forest-priority/ranking")

    assert response.status_code == 404
    assert response.json()["status"] == "not_loaded"
    assert "refresh-ranking" in response.json()["message"]


def test_forest_priority_refresh_ranking(monkeypatch, tmp_path):
    monkeypatch.setenv("GISTDA_API_KEY", "configured-for-test")
    monitored_path = tmp_path / "monitored_forest_areas.json"
    monitored_path.write_text('{"areas": []}', encoding="utf-8")
    ranking_path = tmp_path / "forest_priority_ranking.json"
    monkeypatch.setattr(main_module, "MONITORED_FOREST_AREAS_PATH", monitored_path)
    monkeypatch.setattr(main_module, "FOREST_PRIORITY_RANKING_PATH", ranking_path)
    monkeypatch.setattr(
        main_module,
        "refresh_forest_priority_ranking",
        lambda config_path, output_path, environmental_context_path=None: {
            "status": "ok",
            "message": "Forest priority ranking refreshed.",
            "generated_at": "2026-05-12T00:00:00+00:00",
            "areas": [
                {
                    "rank": 1,
                    "area_id": "AREA-001",
                    "area_name": "Test forest zone",
                    "province": "Chiang Mai",
                    "district": "Chiang Dao",
                    "lat": 19.57651,
                    "lon": 99.01361,
                    "hotspot_count": 1,
                    "dates_available": ["2022-03-28"],
                    "source_satellites_checked": ["suomi-npp"],
                    "landuse_types": ["forest"],
                    "nearest_hotspot_distance_km": 5.82881,
                    "priority_score": 0.64,
                    "severity": "MEDIUM",
                    "recommended_action": "REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE",
                    "operator_summary": "Review the area.",
                    "risk_drivers": ["GISTDA hotspot API context"],
                    "environmental_context": {
                        "temperature_c": 34,
                        "humidity_percent": 35,
                        "wind_speed_kph": 12,
                        "wind_direction": "SW",
                        "rain_probability_percent": 10,
                        "pm25_ugm3": 42.5,
                    },
                    "matched_patterns": [
                        {
                            "pattern_code": "HOTSPOT_NEAR_MONITORED_AREA",
                            "pattern_name": "Hotspot near monitored area",
                            "severity_hint": "MEDIUM",
                            "explanation": "The nearest hotspot is within 10 km of the monitored location.",
                            "recommended_operational_focus": "Check whether local verification is required.",
                        }
                    ],
                }
            ],
        },
    )

    response = client.post("/api/forest-priority/refresh-ranking")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["areas"][0]["rank"] == 1
    assert payload["areas"][0]["priority_score"] == 0.64
    assert payload["areas"][0]["environmental_context"]["temperature_c"] == 34
    assert payload["areas"][0]["matched_patterns"][0]["pattern_code"] == "HOTSPOT_NEAR_MONITORED_AREA"


def test_refresh_hotspot_context_requires_api_key(monkeypatch):
    monkeypatch.delenv("GISTDA_API_KEY", raising=False)

    response = client.post("/api/gistda/refresh-hotspot-context")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_configured",
        "message": "GISTDA_API_KEY environment variable is not configured.",
        "context_path": None,
        "generated_input_path": None,
        "summary": {
            "status": "not_configured",
            "source_satellites_checked": [],
            "hotspot_count": 0,
            "dates_available": [],
            "nearest_hotspot_distance_km": None,
            "provinces_detected": [],
            "landuse_types": [],
            "raw_limited_sample": [],
        },
    }


def test_refresh_hotspot_context_returns_refresh_result(monkeypatch):
    monkeypatch.setenv("GISTDA_API_KEY", "configured-for-test")
    monkeypatch.setattr(
        main_module,
        "refresh_hotspot_context",
        lambda: {
            "status": "ok",
            "message": "GISTDA hotspot context refreshed.",
            "context_path": "live_context/gistda_hotspot_context.json",
            "generated_input_path": "sample_inputs/gistda_wildfire_haze_chiangmai.json",
            "summary": {
                "status": "ok",
                "hotspot_count": 1,
                "dates_available": ["2022-03-28"],
            },
        },
    )

    response = client.post("/api/gistda/refresh-hotspot-context")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["context_path"] == "live_context/gistda_hotspot_context.json"
    assert response.json()["generated_input_path"] == "sample_inputs/gistda_wildfire_haze_chiangmai.json"
    assert response.json()["summary"]["hotspot_count"] == 1


def test_refresh_hotspot_context_surfaces_connector_error(monkeypatch):
    monkeypatch.setenv("GISTDA_API_KEY", "configured-for-test")
    monkeypatch.setattr(
        main_module,
        "refresh_hotspot_context",
        lambda: {
            "status": "error",
            "message": "Upstream GISTDA request failed.",
            "context_path": "live_context/gistda_hotspot_context.json",
            "generated_input_path": "sample_inputs/gistda_wildfire_haze_chiangmai.json",
            "summary": {
                "status": "error",
                "hotspot_count": 0,
            },
        },
    )

    response = client.post("/api/gistda/refresh-hotspot-context")

    assert response.status_code == 502
    assert response.json()["status"] == "error"
    assert response.json()["message"] == "Upstream GISTDA request failed."


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
    assert data["matched_patterns"] == []


def test_incident_score_endpoint_returns_matched_patterns_for_contextual_payload():
    payload = {
        "area_id": "NTH-CHIANGMAI-GISTDA-001",
        "incident_type": "wildfire_haze",
        "hazard_score": 0.51,
        "exposure_score": 0.75,
        "urgency_score": 0.73,
        "confidence": 0.62,
        "risk_drivers": ["GISTDA hotspot API context"],
        "hotspot_count": 1,
        "landuse_types": ["ป่าอนุรักษ์"],
        "nearest_hotspot_distance_km": 5.82881,
    }

    response = client.post("/api/incident/score", json=payload)

    assert response.status_code == 200
    codes = [pattern["pattern_code"] for pattern in response.json()["matched_patterns"]]
    assert codes == ["FOREST_CONSERVATION_PRIORITY", "HOTSPOT_NEAR_MONITORED_AREA"]


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
