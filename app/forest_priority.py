import json
from datetime import datetime, timezone
from pathlib import Path

from app.connectors.gistda_hotspot_api import fetch_hotspot_near_point
from app.models import IncidentScoreRequest
from app.scoring import score_incident
from scripts.fetch_gistda_hotspot_context import (
    build_wildfire_input_from_context,
    write_json,
)


def load_monitored_areas(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def build_ranked_area_result(area: dict, connector_output: dict) -> dict:
    summary = connector_output.get("summary", {})
    scoring_payload = build_wildfire_input_from_context(
        connector_output,
        area_id=area["area_id"],
    )
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
    }


def refresh_forest_priority_ranking(config_path: Path, ranking_path: Path) -> dict:
    configured = load_monitored_areas(config_path)
    ranked_areas = []

    for area in configured.get("areas", []):
        connector_output = fetch_hotspot_near_point(
            lon=area["lon"],
            lat=area["lat"],
            radius=area.get("radius", 1000.5),
        )
        ranked_areas.append(build_ranked_area_result(area, connector_output))

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
