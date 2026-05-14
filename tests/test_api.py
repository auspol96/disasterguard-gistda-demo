from fastapi.testclient import TestClient
import app.main as main_module
from app.main import app

client = TestClient(app)


def test_dashboard_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "ศูนย์ติดตามและจัดลำดับความเสี่ยงไฟป่าและหมอกควันภาคเหนือ" in response.text
    assert "บูรณาการข้อมูลจุดความร้อนและประวัติความเสี่ยงซ้ำซากจาก GISTDA" in response.text
    assert "Real Connector v1" in response.text
    assert "รีเฟรชลำดับความเสี่ยง" in response.text
    assert "พื้นที่เฝ้าระวังทั้งหมด" in response.text
    assert "พื้นที่พบจุดความร้อน" in response.text
    assert "พื้นที่เสี่ยงสูง" in response.text
    assert "พื้นที่เสี่ยงปานกลาง" in response.text
    assert "จุดความร้อนรวม" in response.text
    assert "สรุประดับจังหวัด" in response.text
    assert "คิวปฏิบัติการวันนี้" in response.text
    assert "เร่งประสานงาน" in response.text
    assert "ตรวจสอบภาคสนาม" in response.text
    assert "เฝ้าระวังใกล้ชิด" in response.text
    assert "เฝ้าระวังตามปกติ" in response.text
    assert "แผนที่ลำดับความเสี่ยงพื้นที่ป่าภาคเหนือ" in response.text
    assert "ระดับความเสี่ยง" in response.text
    assert "แสดงเฉพาะพื้นที่ที่พบจุดความร้อน" in response.text
    assert "รายละเอียดพื้นที่ที่เลือก" in response.text
    assert "ระดับการตอบสนองที่แนะนำ" in response.text
    assert "เหตุผลที่อยู่ในลำดับนี้" in response.text
    assert "ประวัติความเสี่ยงซ้ำซากจาก GISTDA" in response.text
    assert "สถานะข้อมูล" in response.text
    assert "แหล่งข้อมูล" in response.text
    assert "แหล่งข้อมูล: GISTDA Hotspot API" in response.text
    assert "แหล่งข้อมูล: GISTDA Recurring Disaster API" in response.text
    assert "สถานะข้อมูล: รอข้อมูล" in response.text
    assert "ข้อมูลสภาพแวดล้อม" not in response.text
    assert "สรุปความเสี่ยงจากสภาพแวดล้อม" not in response.text
    assert "วิธีประเมินความเสี่ยง" in response.text
    assert "ระบบประเมินคะแนนจากจำนวนจุดความร้อน" in response.text
    assert "ปัจจัยที่ส่งผลต่อคะแนน" in response.text
    assert "รูปแบบเหตุการณ์ที่ตรวจพบ" in response.text
    assert "<th>PM2.5</th>" not in response.text
    assert "<th>ลม</th>" not in response.text
    assert "ประวัติซ้ำซาก" in response.text
    assert "ระดับการตอบสนอง" in response.text
    assert "สีเขียว = ต่ำ" in response.text
    assert "สีส้ม = ปานกลาง" in response.text
    assert "สีแดง = สูง" in response.text
    assert "สีแดงเข้ม = วิกฤต" in response.text
    assert "ตัวเลขในวงกลม = ลำดับความเสี่ยง" in response.text
    assert "ตำแหน่งพื้นที่เฝ้าระวังเป็นพิกัดตัวอย่างสำหรับต้นแบบ" in response.text
    assert "lastUpdated" in response.text
    assert "ยังไม่ได้รีเฟรชข้อมูล" in response.text
    assert "provinceFilter" in response.text
    assert "severityFilter" in response.text
    assert "hotspotOnlyFilter" in response.text
    assert "ตารางลำดับความเสี่ยงพื้นที่ป่า" in response.text
    assert "พื้นที่ที่ควรเร่งตรวจสอบ" in response.text
    assert "ภาพรวมประวัติซ้ำซาก" in response.text


def test_static_assets_available():
    js_response = client.get("/static/app.js")
    css_response = client.get("/static/styles.css")
    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "fetch(\"/api/forest-priority/ranking\"" in js_response.text
    assert "fetch(\"/api/forest-priority/refresh-ranking\"" in js_response.text
    assert "refreshRanking" in js_response.text
    assert "renderRanking" in js_response.text
    assert "renderSituationSummary" in js_response.text
    assert "renderProvinceSummary" in js_response.text
    assert "renderActionQueue" in js_response.text
    assert "urgent_coordination" in js_response.text
    assert "renderSelectedArea" in js_response.text
    assert "responsePriorityLabel" in js_response.text
    assert "updateMapTimestamp" in js_response.text
    assert "renderPatternCards" in js_response.text
    assert "selectedRiskDrivers" in js_response.text
    assert "selectedRecurrenceStatus" in js_response.text
    assert "dataSourceStatus" in js_response.text
    assert "recurrenceStatusLabel" in js_response.text
    assert "GISTDA Recurring Disaster API" in js_response.text
    assert "selectedFetchedAt" not in js_response.text
    assert "renderInsights" in js_response.text
    assert "severityFilter" in js_response.text
    assert "hotspotOnlyFilter" in js_response.text
    assert "renderForestPriorityMarkers" in js_response.text
    assert "L.divIcon" in js_response.text
    assert "forest-rank-marker" in js_response.text
    assert "is-selected" in js_response.text
    assert "fitBounds" in js_response.text
    assert "buildForestAreaPopup" in js_response.text
    assert "selectRankedArea" in js_response.text
    assert "populateProvinceFilter" in js_response.text
    assert "filteredRankedAreas" in js_response.text
    assert "ลำดับ" in js_response.text
    assert "ข้อเสนอแนะ" in js_response.text
    assert "color-scheme" in css_response.text
    assert ".map" in css_response.text
    assert ".situation-grid" in css_response.text
    assert ".regional-layout" in css_response.text
    assert ".map-filters" in css_response.text
    assert ".selected-panel" in css_response.text
    assert "max-height: 760px" in css_response.text
    assert "overflow-y: auto" in css_response.text
    assert "align-items: start" in css_response.text
    assert ".selected-detail-grid" in css_response.text
    assert ".environment-detail-grid" in css_response.text
    assert ".pattern-card-list" in css_response.text
    assert ".explanation-panel" in css_response.text
    assert ".insight-grid" in css_response.text
    assert ".hotspot-popup" in css_response.text
    assert ".refresh-message" in css_response.text
    assert ".source-badge-row" in css_response.text
    assert ".ranking-table" in css_response.text
    assert ".province-summary-table" in css_response.text
    assert ".action-queue-grid" in css_response.text
    assert ".action-queue-item" in css_response.text
    assert ".map-legend" in css_response.text
    assert ".map-demo-note" in css_response.text
    assert ".legend-critical" in css_response.text
    assert ".forest-rank-marker" in css_response.text
    assert ".forest-rank-marker.is-top-rank" in css_response.text
    assert ".forest-rank-marker.is-selected" in css_response.text
    assert "L.circleMarker" not in js_response.text


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "DisasterGuard GISTDA Demo"}


def test_forest_priority_areas_endpoint():
    response = client.get("/api/forest-priority/areas")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["areas"]) >= 30
    assert payload["areas"][0]["area_id"] == "NTH-CHIANGDAO-MUEANGNA-001"
    assert payload["areas"][0]["lat"] == 19.57651
    assert payload["areas"][0]["lon"] == 99.01361
    assert payload["areas"][0]["coordinate_status"] == "approximate_demo_coordinate"
    assert all(area["coordinate_status"] == "approximate_demo_coordinate" for area in payload["areas"])
    assert all(3000 <= area["radius"] <= 10000 for area in payload["areas"])
    assert {area["province"] for area in payload["areas"]} == {
        "Chiang Mai",
        "Chiang Rai",
        "Mae Hong Son",
        "Nan",
        "Lampang",
        "Lamphun",
        "Phayao",
        "Phrae",
        "Tak",
    }
    configured_districts = {area["district"] for area in payload["areas"]}
    assert {
        "Samoeng",
        "Mae Suai",
        "Pang Mapha",
        "Mae Charim",
        "Santisuk",
        "Dok Khamtai",
        "Den Chai",
    }.issubset(configured_districts)


def test_forest_priority_ranking_missing(monkeypatch, tmp_path):
    missing_path = tmp_path / "forest_priority_ranking.json"
    monkeypatch.setattr(main_module, "FOREST_PRIORITY_RANKING_PATH", missing_path)

    response = client.get("/api/forest-priority/ranking")

    assert response.status_code == 404
    assert response.json()["status"] == "not_loaded"
    assert "refresh-ranking" in response.json()["message"]


def test_forest_priority_ranking_not_found_recurrence_hides_confirmed_counts(monkeypatch, tmp_path):
    ranking_path = tmp_path / "forest_priority_ranking.json"
    ranking_path.write_text(
        """
        {
          "status": "ok",
          "areas": [
            {
              "rank": 1,
              "area_id": "AREA-001",
              "area_name": "Test forest zone",
              "province": "Chiang Mai",
              "district": "Chiang Dao",
              "lat": 19.57651,
              "lon": 99.01361,
              "hotspot_count": 0,
              "landuse_types": [],
              "nearest_hotspot_distance_km": null,
              "priority_score": 0.2,
              "severity": "LOW",
              "risk_drivers": ["พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA"],
              "matched_patterns": [{"pattern_code": "RECURRENT_RISK_AREA"}],
              "recurrence_context": {
                "source": "gistda_recurring_api",
                "status": "not_found",
                "records": []
              }
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setattr(main_module, "FOREST_PRIORITY_RANKING_PATH", ranking_path)

    response = client.get("/api/forest-priority/ranking")

    assert response.status_code == 200
    area = response.json()["areas"][0]
    assert area["recurrence_context"]["status"] == "not_found"
    assert area["recurrence_context"]["recurrence_score"] is None
    assert "hotspot_recurrence_count" not in area["recurrence_context"]
    assert "ยังไม่พบข้อมูลประวัติความเสี่ยงซ้ำซากจาก GISTDA" in area["recurrence_context"]["recurrence_summary_th"]
    assert "พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA" not in area["risk_drivers"]
    assert area["matched_patterns"] == []
    assert response.json()["action_queue"]["routine_monitoring"][0]["area_id"] == "AREA-001"


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
        lambda config_path, output_path, environmental_context_path=None, recurrence_context_path=None: {
            "status": "ok",
            "message": "Forest priority ranking refreshed.",
            "generated_at": "2026-05-12T00:00:00+00:00",
            "province_summary": [
                {
                    "province": "Chiang Mai",
                    "total_areas": 1,
                    "high_count": 0,
                    "medium_count": 1,
                    "low_count": 0,
                    "total_hotspots": 1,
                    "highest_rank_area": {"rank": 1, "area_name": "Test forest zone"},
                    "highest_priority_score": 0.64,
                    "province_priority_level": "MEDIUM",
                }
            ],
            "action_queue": {
                "urgent_coordination": [],
                "field_verification": [
                    {
                        "rank": 1,
                        "area_id": "AREA-001",
                        "area_name": "Test forest zone",
                        "province": "Chiang Mai",
                        "district": "Chiang Dao",
                        "hotspot_count": 1,
                        "severity": "MEDIUM",
                        "priority_score": 0.64,
                        "reason_th": "พบจุดความร้อน 1 จุด ควรตรวจสอบภาคสนาม",
                        "explainable_ranking_th": "พื้นที่นี้อยู่ลำดับที่ 1 เนื่องจากพบจุดความร้อน 1 จุด",
                    }
                ],
                "close_monitoring": [],
                "routine_monitoring": [],
            },
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
                    "response_priority": "FIELD_VERIFICATION",
                    "explainable_ranking_th": "พื้นที่นี้อยู่ลำดับที่ 1 เนื่องจากพบจุดความร้อน 1 จุด",
                    "operator_summary": "Review the area.",
                    "risk_drivers": ["GISTDA hotspot API context"],
                    "recurrence_context": {
                        "source": "gistda_recurring_api",
                        "status": "ok",
                        "hotspot_recurrence_count": 2,
                        "flood_recurrence_count": 0,
                        "drought_recurrence_count": 1,
                        "recurrence_score": 0.12,
                        "recurrence_summary_th": "มีประวัติซ้ำซากระดับต่ำ",
                    },
                    "environmental_context": {},
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
    assert payload["areas"][0]["recurrence_context"]["recurrence_score"] == 0.12
    assert payload["areas"][0]["response_priority"] == "FIELD_VERIFICATION"
    assert "ลำดับที่ 1" in payload["areas"][0]["explainable_ranking_th"]
    assert payload["province_summary"][0]["province"] == "Chiang Mai"
    assert payload["province_summary"][0]["highest_priority_score"] == 0.64
    assert payload["action_queue"]["field_verification"][0]["area_id"] == "AREA-001"
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
