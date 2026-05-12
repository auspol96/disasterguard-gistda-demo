from app.forest_priority import build_ranked_area_result


def test_zero_hotspot_ranked_area_uses_low_operational_calibration():
    area = {
        "area_id": "NTH-CLEAR-001",
        "area_name": "Clear monitored forest radius",
        "province": "Chiang Mai",
        "district": "Mae Rim",
        "lat": 18.9184,
        "lon": 98.9397,
    }
    connector_output = {
        "status": "ok",
        "summary": {
            "status": "ok",
            "source_satellites_checked": ["terra", "aqua", "suomi-npp"],
            "hotspot_count": 0,
            "dates_available": [],
            "nearest_hotspot_distance_km": None,
            "provinces_detected": [],
            "landuse_types": [],
            "raw_limited_sample": [],
        },
    }

    ranked = build_ranked_area_result(area, connector_output)

    assert 0.15 <= ranked["priority_score"] <= 0.25
    assert ranked["severity"] == "LOW"
    assert ranked["recommended_action"] == "CONTINUE_ROUTINE_MONITORING"
    assert "No hotspot was detected in the monitored radius" in ranked["operator_summary"]
    assert "GISTDA checked, no hotspot detected in monitored radius" in ranked["risk_drivers"]
    assert ranked["matched_patterns"][0]["pattern_code"] == "NO_HOTSPOT_ROUTINE_MONITORING"
