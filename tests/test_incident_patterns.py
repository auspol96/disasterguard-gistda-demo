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
