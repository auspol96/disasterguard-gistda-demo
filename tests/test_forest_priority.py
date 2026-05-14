from pathlib import Path

from app.forest_priority import (
    action_queue_group_for_area,
    build_action_queue,
    build_change_summary,
    build_province_summary,
    build_ranked_area_result,
    determine_response_priority,
    previous_ranking_path_for,
    refresh_forest_priority_ranking,
)
from app.recurrence_context import (
    NO_DATA_MESSAGE,
    calculate_recurrence_score,
    normalize_gistda_recurrence_response,
)


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


def test_ranked_area_ignores_non_gistda_environmental_context_and_uses_gistda_recurrence():
    area = {
        "area_id": "NTH-ENV-001",
        "area_name": "Dry monitored forest radius",
        "province": "Chiang Mai",
        "district": "Mae Taeng",
        "lat": 19.1173,
        "lon": 98.9415,
    }
    connector_output = {
        "status": "ok",
        "summary": {
            "status": "ok",
            "source_satellites_checked": ["suomi-npp"],
            "hotspot_count": 1,
            "dates_available": ["2022-03-28"],
            "nearest_hotspot_distance_km": 5.0,
            "provinces_detected": ["Chiang Mai"],
            "landuse_types": ["ป่าอนุรักษ์"],
            "raw_limited_sample": [{"frequency": 1}],
        },
    }
    environmental_context = {
        "temperature_c": 34,
        "humidity_percent": 30,
        "wind_speed_kph": 12,
        "wind_direction": "SW",
        "rain_probability_percent": 10,
        "pm25_ugm3": 42.5,
    }

    recurrence_context = {
        "source": "gistda_recurring_api",
        "status": "ok",
        "records": [
            {"type": "hotspot"},
            {"type": "hotspot"},
            {"type": "hotspot"},
            {"type": "hotspot"},
            {"type": "flood"},
            {"type": "drought"},
            {"type": "drought"},
        ],
    }

    ranked = build_ranked_area_result(area, connector_output, environmental_context, recurrence_context)
    codes = [pattern["pattern_code"] for pattern in ranked["matched_patterns"]]

    assert ranked["environmental_context"] == {}
    assert ranked["environmental_risk_summary"] == {}
    assert "DRY_WEATHER_FIRE_SPREAD_RISK" not in codes
    assert "WIND_SPREAD_WATCH" not in codes
    assert "HAZE_HEALTH_RISK" not in codes
    assert "HOTSPOT_PLUS_DRY_WEATHER" not in codes
    assert ranked["priority_score"] > 0.64
    assert ranked["recurrence_context"]["hotspot_recurrence_count"] == 4
    assert ranked["recurrence_context"]["recurrence_score"] > 0
    assert "พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA" in ranked["risk_drivers"]
    assert "RECURRENT_RISK_AREA" in codes


def test_no_sample_recurrence_file_is_used():
    repo_root = Path(__file__).resolve().parents[1]

    assert not (repo_root / "config" / "recurrence_context_samples.json").exists()


def test_not_found_recurrence_does_not_show_zero_counts_as_evidence():
    normalized = normalize_gistda_recurrence_response(
        {"source": "gistda_recurring_api", "status": "not_found", "records": []}
    )

    assert normalized["status"] == "not_found"
    assert normalized["recurrence_score"] is None
    assert normalized["recurrence_summary_th"] == NO_DATA_MESSAGE
    assert "hotspot_recurrence_count" not in normalized
    assert "flood_recurrence_count" not in normalized
    assert "drought_recurrence_count" not in normalized


def test_recurrence_affects_score_only_when_gistda_status_ok():
    area = {
        "area_id": "NTH-RECURRENCE-001",
        "area_name": "Recurring risk check",
        "province": "Chiang Mai",
        "district": "Chiang Dao",
        "lat": 19.57651,
        "lon": 99.01361,
    }
    connector_output = {
        "status": "ok",
        "summary": {
            "status": "ok",
            "source_satellites_checked": ["suomi-npp"],
            "hotspot_count": 0,
            "dates_available": [],
            "nearest_hotspot_distance_km": None,
            "provinces_detected": [],
            "landuse_types": [],
            "raw_limited_sample": [],
        },
    }

    not_found = build_ranked_area_result(
        area,
        connector_output,
        recurrence_context={"source": "gistda_recurring_api", "status": "not_found", "records": []},
    )
    ok = build_ranked_area_result(
        area,
        connector_output,
        recurrence_context={
            "source": "gistda_recurring_api",
            "status": "ok",
            "records": [{"type": "hotspot"}, {"type": "hotspot"}, {"type": "drought"}],
        },
    )

    assert not_found["recurrence_context"]["recurrence_score"] is None
    assert "พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA" not in not_found["risk_drivers"]
    assert ok["priority_score"] > not_found["priority_score"]
    assert "พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA" in ok["risk_drivers"]


def test_open_meteo_data_is_not_used_in_official_score():
    area = {
        "area_id": "NTH-NON-GISTDA-ENV-001",
        "area_name": "Non-GISTDA environment ignored",
        "province": "Chiang Mai",
        "district": "Mae Taeng",
        "lat": 19.1173,
        "lon": 98.9415,
    }
    connector_output = {
        "status": "ok",
        "summary": {
            "status": "ok",
            "source_satellites_checked": ["suomi-npp"],
            "hotspot_count": 1,
            "dates_available": ["2022-03-28"],
            "nearest_hotspot_distance_km": 5.0,
            "provinces_detected": ["Chiang Mai"],
            "landuse_types": ["ป่าอนุรักษ์"],
            "raw_limited_sample": [{"frequency": 1}],
        },
    }
    open_meteo_context = {
        "source": "open-meteo",
        "temperature_c": 40,
        "humidity_percent": 10,
        "wind_speed_kph": 30,
        "pm25_ugm3": 90,
    }

    without_environment = build_ranked_area_result(area, connector_output)
    with_open_meteo = build_ranked_area_result(area, connector_output, open_meteo_context)

    assert with_open_meteo["priority_score"] == without_environment["priority_score"]
    assert with_open_meteo["environmental_context"] == {}
    assert with_open_meteo["environmental_risk_summary"] == {}
    assert "dry weather fire spread risk" not in with_open_meteo["risk_drivers"]
    assert "PM2.5 haze health risk" not in with_open_meteo["risk_drivers"]


def test_recurrence_score_calculation():
    assert calculate_recurrence_score(0, 0, 0) == 0
    assert calculate_recurrence_score(4, 1, 2) == 0.26
    assert calculate_recurrence_score(99, 99, 99) == 0.3


def test_response_priority_mapping():
    assert determine_response_priority({"severity": "LOW", "hotspot_count": 0}) == "ROUTINE_MONITORING"
    assert determine_response_priority(
        {
            "severity": "LOW",
            "hotspot_count": 0,
            "recurrence_context": {
                "source": "gistda_recurring_api",
                "status": "not_found",
                "recurrence_score": 0.12,
            },
        }
    ) == "ROUTINE_MONITORING"
    assert determine_response_priority(
        {
            "severity": "LOW",
            "hotspot_count": 0,
            "recurrence_context": {
                "source": "gistda_recurring_api",
                "status": "ok",
                "recurrence_score": 0.12,
            },
        }
    ) == "WATCHLIST"
    assert determine_response_priority(
        {"severity": "MEDIUM", "hotspot_count": 1, "recurrence_context": {"recurrence_score": 0}}
    ) == "FIELD_VERIFICATION"
    assert determine_response_priority({"severity": "HIGH", "hotspot_count": 1}) == "URGENT_COORDINATION"


def test_province_summary_aggregation_and_explainable_fields():
    ranked_areas = [
        {
            "rank": 1,
            "area_id": "A",
            "area_name": "Area A",
            "province": "Chiang Mai",
            "severity": "CRITICAL",
            "hotspot_count": 3,
            "priority_score": 0.8,
        },
        {
            "rank": 2,
            "area_id": "B",
            "area_name": "Area B",
            "province": "Chiang Mai",
            "severity": "MEDIUM",
            "hotspot_count": 1,
            "priority_score": 0.5,
        },
        {
            "rank": 3,
            "area_id": "C",
            "area_name": "Area C",
            "province": "Nan",
            "severity": "LOW",
            "hotspot_count": 0,
            "priority_score": 0.2,
        },
    ]

    summary = build_province_summary(ranked_areas)
    chiang_mai = next(item for item in summary if item["province"] == "Chiang Mai")

    assert chiang_mai["total_areas"] == 2
    assert chiang_mai["critical_count"] == 1
    assert chiang_mai["high_count"] == 0
    assert chiang_mai["medium_count"] == 1
    assert chiang_mai["total_hotspots"] == 4
    assert chiang_mai["highest_rank_area"]["area_name"] == "Area A"
    assert chiang_mai["highest_priority_score"] == 0.8
    assert chiang_mai["province_priority_level"] == "CRITICAL"


def test_action_queue_grouping_and_reason_fields():
    ranked_areas = [
        {
            "rank": 1,
            "area_id": "HIGH",
            "area_name": "High area",
            "province": "Chiang Mai",
            "district": "Chiang Dao",
            "severity": "HIGH",
            "hotspot_count": 0,
            "priority_score": 0.8,
            "explainable_ranking_th": "เหตุผลลำดับสูง",
        },
        {
            "rank": 2,
            "area_id": "MED",
            "area_name": "Medium hotspot area",
            "province": "Nan",
            "district": "Pua",
            "severity": "MEDIUM",
            "hotspot_count": 1,
            "priority_score": 0.6,
            "explainable_ranking_th": "พบจุดความร้อน",
        },
        {
            "rank": 3,
            "area_id": "LOW-HOT",
            "area_name": "Low hotspot area",
            "province": "Tak",
            "district": "Umphang",
            "severity": "LOW",
            "hotspot_count": 1,
            "priority_score": 0.3,
        },
        {
            "rank": 4,
            "area_id": "LOW-CLEAR",
            "area_name": "Low clear area",
            "province": "Phrae",
            "district": "Long",
            "severity": "LOW",
            "hotspot_count": 0,
            "priority_score": 0.2,
            "recurrence_context": {"status": "not_found"},
        },
    ]

    queue = build_action_queue(ranked_areas)

    assert action_queue_group_for_area(ranked_areas[0]) == "urgent_coordination"
    assert action_queue_group_for_area(ranked_areas[1]) == "field_verification"
    assert action_queue_group_for_area(ranked_areas[2]) == "close_monitoring"
    assert action_queue_group_for_area(ranked_areas[3]) == "routine_monitoring"
    assert queue["urgent_coordination"][0]["area_id"] == "HIGH"
    assert queue["field_verification"][0]["short_reason_th"] == "พบจุดความร้อน 1 จุด ควรตรวจสอบภาคสนาม"
    assert "recommended_action" in queue["field_verification"][0]
    assert queue["close_monitoring"][0]["area_id"] == "LOW-HOT"
    assert queue["routine_monitoring"][0]["area_id"] == "LOW-CLEAR"


def test_change_summary_detects_hotspot_and_severity_increases():
    previous = {
        "areas": [
            {
                "rank": 4,
                "area_id": "AREA-001",
                "area_name": "Chiang Dao watch",
                "province": "Chiang Mai",
                "district": "Chiang Dao",
                "hotspot_count": 2,
                "severity": "MEDIUM",
            }
        ]
    }
    current = {
        "areas": [
            {
                "rank": 1,
                "area_id": "AREA-001",
                "area_name": "Chiang Dao watch",
                "province": "Chiang Mai",
                "district": "Chiang Dao",
                "hotspot_count": 6,
                "severity": "HIGH",
            }
        ]
    }

    summary = build_change_summary(current, previous)

    assert summary["status"] == "ok"
    assert summary["increased_hotspot_areas"][0]["change_reason_th"] == "จำนวนจุดความร้อนเพิ่มจาก 2 เป็น 6"
    assert summary["severity_increased_areas"][0]["change_reason_th"] == "ระดับความเสี่ยงเพิ่มจาก MEDIUM เป็น HIGH"
    assert summary["rank_improved_areas"][0]["change_reason_th"] == "อันดับความเสี่ยงสูงขึ้นจาก 4 เป็น 1"


def test_change_summary_no_previous_file_case():
    summary = build_change_summary({"areas": []}, None)

    assert summary["status"] == "no_previous"
    assert summary["message"] == "ยังไม่มีข้อมูลรอบก่อนหน้าเพื่อเปรียบเทียบ"
    assert summary["new_hotspot_areas"] == []


def test_refresh_ranking_does_not_load_sample_environmental_context(monkeypatch, tmp_path):
    monitored_path = tmp_path / "monitored_forest_areas.json"
    monitored_path.write_text(
        """
        {
          "areas": [
            {
              "area_id": "NTH-CHIANGDAO-MUEANGNA-001",
              "area_name": "Chiang Dao / Mueang Na forest watch",
              "province": "Chiang Mai",
              "district": "Chiang Dao",
              "lat": 19.57651,
              "lon": 99.01361,
              "radius": 1000.5
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    environmental_path = tmp_path / "environmental_context_samples.json"
    environmental_path.write_text(
        """
        {
          "NTH-CHIANGDAO-MUEANGNA-001": {
            "temperature_c": 34.2,
            "humidity_percent": 34,
            "wind_speed_kph": 12,
            "wind_direction": "SW",
            "rain_probability_percent": 10,
            "pm25_ugm3": 42.5
          }
        }
        """,
        encoding="utf-8",
    )
    ranking_path = tmp_path / "forest_priority_ranking.json"

    monkeypatch.setattr(
        "app.forest_priority.fetch_hotspot_near_point",
        lambda lon, lat, radius: {
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
        },
    )
    monkeypatch.setattr(
        "app.environmental_context.fetch_open_meteo_environment",
        lambda lat, lon: {"status": "error", "message": "offline"},
    )

    ranking = refresh_forest_priority_ranking(
        monitored_path,
        ranking_path,
        environmental_path,
    )

    assert ranking["areas"][0]["environmental_context"] == {}
    assert ranking["areas"][0]["environmental_risk_summary"] == {}
    assert "province_summary" in ranking
    assert "action_queue" in ranking
    assert "explainable_ranking_th" in ranking["areas"][0]
    assert "response_priority" in ranking["areas"][0]
    assert "recurrence_context" in ranking["areas"][0]
    assert ranking["areas"][0]["change_status_th"] == "ยังไม่มีข้อมูลรอบก่อนหน้า"
    assert ranking["change_summary"]["status"] == "no_previous"


def test_refresh_ranking_saves_previous_file_and_generates_change_summary(monkeypatch, tmp_path):
    monitored_path = tmp_path / "monitored_forest_areas.json"
    monitored_path.write_text(
        """
        {
          "areas": [
            {
              "area_id": "AREA-001",
              "area_name": "Chiang Dao watch",
              "province": "Chiang Mai",
              "district": "Chiang Dao",
              "lat": 19.57651,
              "lon": 99.01361,
              "radius": 1000.5
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    ranking_path = tmp_path / "forest_priority_ranking.json"
    ranking_path.write_text(
        """
        {
          "status": "ok",
          "areas": [
            {
              "rank": 4,
              "area_id": "AREA-001",
              "area_name": "Chiang Dao watch",
              "province": "Chiang Mai",
              "district": "Chiang Dao",
              "hotspot_count": 0,
              "severity": "LOW"
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "app.forest_priority.fetch_hotspot_near_point",
        lambda lon, lat, radius: {
            "status": "ok",
            "summary": {
                "status": "ok",
                "source_satellites_checked": ["suomi-npp"],
                "hotspot_count": 1,
                "dates_available": ["2022-03-28"],
                "nearest_hotspot_distance_km": 5.0,
                "provinces_detected": ["Chiang Mai"],
                "landuse_types": ["ป่าอนุรักษ์"],
                "raw_limited_sample": [{"frequency": 1}],
            },
        },
    )

    ranking = refresh_forest_priority_ranking(monitored_path, ranking_path)
    previous_path = previous_ranking_path_for(ranking_path)

    assert previous_path.exists()
    assert '"rank": 4' in previous_path.read_text(encoding="utf-8")
    assert ranking["change_summary"]["new_hotspot_areas"][0]["area_id"] == "AREA-001"
    assert ranking["areas"][0]["change_status_th"] in {
        "อันดับดีขึ้นจาก 4 เป็น 1",
        "จำนวนจุดความร้อนเพิ่มจาก 0 เป็น 1",
        "ระดับความเสี่ยงเพิ่มจาก LOW เป็น MEDIUM",
    }


def test_refresh_ranking_does_not_use_open_meteo_environmental_context(monkeypatch, tmp_path):
    monitored_path = tmp_path / "monitored_forest_areas.json"
    monitored_path.write_text(
        """
        {
          "areas": [
            {
              "area_id": "NTH-CHIANGDAO-MUEANGNA-001",
              "area_name": "Chiang Dao / Mueang Na forest watch",
              "province": "Chiang Mai",
              "district": "Chiang Dao",
              "lat": 19.57651,
              "lon": 99.01361,
              "radius": 1000.5
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    environmental_path = tmp_path / "environmental_context_samples.json"
    environmental_path.write_text('{"NTH-CHIANGDAO-MUEANGNA-001": {"temperature_c": 30}}', encoding="utf-8")
    ranking_path = tmp_path / "forest_priority_ranking.json"

    monkeypatch.setattr(
        "app.forest_priority.fetch_hotspot_near_point",
        lambda lon, lat, radius: {
            "status": "ok",
            "summary": {
                "status": "ok",
                "source_satellites_checked": ["suomi-npp"],
                "hotspot_count": 1,
                "dates_available": ["2022-03-28"],
                "nearest_hotspot_distance_km": 5.0,
                "provinces_detected": ["Chiang Mai"],
                "landuse_types": ["ป่าอนุรักษ์"],
                "raw_limited_sample": [{"frequency": 1}],
            },
        },
    )
    monkeypatch.setattr(
        "app.environmental_context.fetch_open_meteo_environment",
        lambda lat, lon: {
            "status": "ok",
            "source": "open-meteo",
            "temperature_c": 34,
            "humidity_percent": 30,
            "wind_speed_kph": 12,
            "wind_direction": "SW",
            "rain_probability_percent": 10,
            "pm25_ugm3": 42.5,
            "fetched_at": "2026-05-13T00:00:00+00:00",
        },
    )

    ranking = refresh_forest_priority_ranking(monitored_path, ranking_path, environmental_path)

    assert ranking["areas"][0]["environmental_context"] == {}
    assert ranking["areas"][0]["environmental_risk_summary"] == {}
    assert "dry weather fire spread risk" not in ranking["areas"][0]["risk_drivers"]
    assert "PM2.5 haze health risk" not in ranking["areas"][0]["risk_drivers"]
