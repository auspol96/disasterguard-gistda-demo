from app.forest_priority import build_ranked_area_result, refresh_forest_priority_ranking


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


def test_ranked_area_includes_environmental_context_and_patterns():
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

    ranked = build_ranked_area_result(area, connector_output, environmental_context)
    codes = [pattern["pattern_code"] for pattern in ranked["matched_patterns"]]

    assert ranked["environmental_context"] == environmental_context
    assert "DRY_WEATHER_FIRE_SPREAD_RISK" in codes
    assert "WIND_SPREAD_WATCH" in codes
    assert "HAZE_HEALTH_RISK" in codes
    assert "HOTSPOT_PLUS_DRY_WEATHER" in codes
    assert ranked["priority_score"] > 0.64


def test_refresh_ranking_loads_environmental_context_from_direct_mapping(monkeypatch, tmp_path):
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

    assert ranking["areas"][0]["environmental_context"]["temperature_c"] == 34.2
    assert ranking["areas"][0]["environmental_context"]


def test_refresh_ranking_uses_live_environmental_context_when_available(monkeypatch, tmp_path):
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

    assert ranking["areas"][0]["environmental_context"]["source"] == "open-meteo"
    assert ranking["areas"][0]["environmental_context"]["temperature_c"] == 34
