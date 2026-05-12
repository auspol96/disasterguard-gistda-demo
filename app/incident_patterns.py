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
) -> list[dict[str, str]]:
    count = hotspot_count or 0
    landuse = landuse_types or []
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

    return patterns
