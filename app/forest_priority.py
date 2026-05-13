import json
from datetime import datetime, timezone
from pathlib import Path

from app.connectors.gistda_hotspot_api import fetch_hotspot_near_point
from app.environmental_context import get_environmental_context_for_area
from app.models import IncidentScoreRequest
from app.scoring import score_incident
from scripts.fetch_gistda_hotspot_context import (
    build_wildfire_input_from_context,
    write_json,
)


def load_monitored_areas(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def enrich_scoring_payload_with_environment(scoring_payload: dict, environmental_context: dict) -> dict:
    enriched = dict(scoring_payload)
    hotspot_count = int(enriched.get("hotspot_count") or 0)
    temperature = environmental_context.get("temperature_c")
    humidity = environmental_context.get("humidity_percent")
    wind_speed = environmental_context.get("wind_speed_kph")
    pm25 = environmental_context.get("pm25_ugm3")
    is_dry_weather = (
        humidity is not None
        and temperature is not None
        and humidity < 40
        and temperature >= 32
    )

    if is_dry_weather:
        enriched["hazard_score"] = _clamp(enriched["hazard_score"] + 0.05)
        enriched["urgency_score"] = _clamp(enriched["urgency_score"] + 0.03)
        enriched.setdefault("risk_drivers", []).append("dry weather fire spread risk")

    if wind_speed is not None and wind_speed >= 10:
        enriched["urgency_score"] = _clamp(enriched["urgency_score"] + 0.04)
        enriched.setdefault("risk_drivers", []).append("wind spread watch")

    if pm25 is not None and pm25 >= 37.5:
        enriched["exposure_score"] = _clamp(enriched["exposure_score"] + 0.08)
        enriched["urgency_score"] = _clamp(enriched["urgency_score"] + 0.02)
        enriched.setdefault("risk_drivers", []).append("PM2.5 haze health risk")

    if hotspot_count > 0 and is_dry_weather:
        enriched["hazard_score"] = _clamp(enriched["hazard_score"] + 0.10)
        enriched["urgency_score"] = _clamp(enriched["urgency_score"] + 0.08)
        enriched.setdefault("risk_drivers", []).append("hotspot plus dry weather")

    enriched["environmental_context"] = environmental_context
    return enriched


def build_ranked_area_result(
    area: dict,
    connector_output: dict,
    environmental_context: dict | None = None,
) -> dict:
    summary = connector_output.get("summary", {})
    environmental_context = environmental_context or {}
    scoring_payload = build_wildfire_input_from_context(
        connector_output,
        area_id=area["area_id"],
    )
    scoring_payload = enrich_scoring_payload_with_environment(scoring_payload, environmental_context)
    scored = score_incident(IncidentScoreRequest(**scoring_payload))
    sample = (summary.get("raw_limited_sample") or [{}])[0]

    return {
        "area_id": area["area_id"],
        "area_name": area["area_name"],
        "province": area.get("province") or sample.get("province"),
        "district": area.get("district") or sample.get("district"),
        "lat": area["lat"],
        "lon": area["lon"],
        "hotspot_count": summary.get("hotspot_count", 0),
        "dates_available": summary.get("dates_available", []),
        "source_satellites_checked": summary.get("source_satellites_checked", []),
        "landuse_types": summary.get("landuse_types", []),
        "nearest_hotspot_distance_km": summary.get("nearest_hotspot_distance_km"),
        "priority_score": scored.priority_score,
        "severity": scored.severity,
        "recommended_action": scored.recommended_action,
        "operator_summary": scored.operator_summary,
        "risk_drivers": scored.risk_drivers,
        "matched_patterns": [pattern.model_dump() for pattern in scored.matched_patterns],
        "environmental_context": environmental_context,
    }


def refresh_forest_priority_ranking(
    config_path: Path,
    ranking_path: Path,
    environmental_context_path: Path | None = None,
) -> dict:
    configured = load_monitored_areas(config_path)
    ranked_areas = []

    for area in configured.get("areas", []):
        connector_output = fetch_hotspot_near_point(
            lon=area["lon"],
            lat=area["lat"],
            radius=area.get("radius", 1000.5),
        )
        environmental_context = (
            get_environmental_context_for_area(
                area["area_id"],
                environmental_context_path,
                lat=area["lat"],
                lon=area["lon"],
            )
            if environmental_context_path
            else {}
        )
        ranked_areas.append(build_ranked_area_result(area, connector_output, environmental_context))

    ranked_areas.sort(key=lambda item: item["priority_score"], reverse=True)
    for index, item in enumerate(ranked_areas, start=1):
        item["rank"] = index

    payload = {
        "status": "ok",
        "message": "Forest priority ranking refreshed.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "areas": ranked_areas,
    }
    write_json(ranking_path, payload)
    return payload
