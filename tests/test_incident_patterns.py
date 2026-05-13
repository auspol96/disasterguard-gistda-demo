from app.incident_patterns import match_wildfire_haze_patterns


def test_zero_hotspot_matches_routine_monitoring_pattern():
    patterns = match_wildfire_haze_patterns(0, [], None)

    assert [pattern["pattern_code"] for pattern in patterns] == ["NO_HOTSPOT_ROUTINE_MONITORING"]


def test_conservation_forest_hotspot_matches_priority_pattern():
    patterns = match_wildfire_haze_patterns(1, ["ป่าอนุรักษ์"], 15.0)

    assert "FOREST_CONSERVATION_PRIORITY" in [pattern["pattern_code"] for pattern in patterns]


def test_near_hotspot_matches_near_monitored_area_pattern():
    patterns = match_wildfire_haze_patterns(1, ["forest"], 10.0)

    assert "HOTSPOT_NEAR_MONITORED_AREA" in [pattern["pattern_code"] for pattern in patterns]


def test_multi_hotspot_cluster_pattern_matches_three_or_more_hotspots():
    patterns = match_wildfire_haze_patterns(3, ["forest"], 12.0)

    assert "MULTI_HOTSPOT_CLUSTER" in [pattern["pattern_code"] for pattern in patterns]


def test_dry_weather_pattern_matches_low_humidity_high_temperature():
    patterns = match_wildfire_haze_patterns(
        0,
        [],
        None,
        {"temperature_c": 33, "humidity_percent": 35},
    )

    assert "DRY_WEATHER_FIRE_SPREAD_RISK" in [pattern["pattern_code"] for pattern in patterns]


def test_wind_pattern_matches_elevated_wind_speed():
    patterns = match_wildfire_haze_patterns(0, [], None, {"wind_speed_kph": 10})

    assert "WIND_SPREAD_WATCH" in [pattern["pattern_code"] for pattern in patterns]


def test_pm25_pattern_matches_haze_health_threshold():
    patterns = match_wildfire_haze_patterns(0, [], None, {"pm25_ugm3": 37.5})

    assert "HAZE_HEALTH_RISK" in [pattern["pattern_code"] for pattern in patterns]


def test_hotspot_plus_dry_weather_pattern_requires_hotspot_and_dry_weather():
    patterns = match_wildfire_haze_patterns(
        1,
        ["forest"],
        12.0,
        {"temperature_c": 34, "humidity_percent": 30},
    )

    assert "HOTSPOT_PLUS_DRY_WEATHER" in [pattern["pattern_code"] for pattern in patterns]
