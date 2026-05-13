from typing import Any


def _pattern(
    pattern_code: str,
    pattern_name: str,
    severity_hint: str,
    explanation: str,
    recommended_operational_focus: str,
) -> dict[str, str]:
    return {
        "pattern_code": pattern_code,
        "pattern_name": pattern_name,
        "severity_hint": severity_hint,
        "explanation": explanation,
        "recommended_operational_focus": recommended_operational_focus,
    }


def match_wildfire_haze_patterns(
    hotspot_count: int | None,
    landuse_types: list[str] | None,
    nearest_hotspot_distance_km: float | None,
    environmental_context: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    count = hotspot_count or 0
    landuse = landuse_types or []
    environment = environmental_context or {}
    patterns: list[dict[str, str]] = []

    if hotspot_count == 0:
        patterns.append(
            _pattern(
                "NO_HOTSPOT_ROUTINE_MONITORING",
                "No hotspot detected in monitored radius",
                "LOW",
                "GISTDA checked this monitored area and no hotspot was detected within the configured radius.",
                "Continue routine monitoring.",
            )
        )

    if count > 0 and "ป่าอนุรักษ์" in landuse:
        patterns.append(
            _pattern(
                "FOREST_CONSERVATION_PRIORITY",
                "Conservation forest hotspot priority",
                "MEDIUM",
                "A hotspot was detected in a conservation forest area.",
                "Review with forest protection or local response team.",
            )
        )

    if nearest_hotspot_distance_km is not None and nearest_hotspot_distance_km <= 10:
        patterns.append(
            _pattern(
                "HOTSPOT_NEAR_MONITORED_AREA",
                "Hotspot near monitored area",
                "MEDIUM",
                "The nearest hotspot is within 10 km of the monitored location.",
                "Check whether local verification is required.",
            )
        )

    if count >= 3:
        patterns.append(
            _pattern(
                "MULTI_HOTSPOT_CLUSTER",
                "Multiple hotspot cluster",
                "HIGH",
                "Multiple hotspots were detected in the monitored area.",
                "Escalate for coordinated review.",
            )
        )

    temperature = environment.get("temperature_c")
    humidity = environment.get("humidity_percent")
    wind_speed = environment.get("wind_speed_kph")
    pm25 = environment.get("pm25_ugm3")
    is_dry_weather = (
        humidity is not None
        and temperature is not None
        and humidity < 40
        and temperature >= 32
    )

    if is_dry_weather:
        patterns.append(
            _pattern(
                "DRY_WEATHER_FIRE_SPREAD_RISK",
                "Dry weather fire spread risk",
                "MEDIUM",
                "Low humidity and high temperature may increase fire spread potential.",
                "Watch for rapid drying and review local fire spread conditions.",
            )
        )

    if wind_speed is not None and wind_speed >= 10:
        patterns.append(
            _pattern(
                "WIND_SPREAD_WATCH",
                "Wind spread watch",
                "MEDIUM",
                "Wind speed is high enough to support smoke or fire spread.",
                "Review wind direction and nearby exposure before field coordination.",
            )
        )

    if pm25 is not None and pm25 >= 37.5:
        patterns.append(
            _pattern(
                "HAZE_HEALTH_RISK",
                "Haze health risk",
                "MEDIUM",
                "PM2.5 is elevated and may indicate haze health concern.",
                "Consider public-health awareness or haze monitoring coordination.",
            )
        )

    if count > 0 and is_dry_weather:
        patterns.append(
            _pattern(
                "HOTSPOT_PLUS_DRY_WEATHER",
                "Hotspot plus dry weather",
                "HIGH",
                "A detected hotspot is coinciding with dry weather conditions.",
                "Prioritize review for possible fire spread and response coordination.",
            )
        )

    return patterns
