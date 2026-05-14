import json
from datetime import datetime, timezone
from pathlib import Path

from app.connectors.gistda_hotspot_api import fetch_hotspot_near_point
from app.models import IncidentScoreRequest
from app.recurrence_context import (
    get_recurrence_context_for_area,
    is_confirmed_gistda_recurrence,
    normalize_gistda_recurrence_response,
)
from app.scoring import score_incident
from scripts.fetch_gistda_hotspot_context import (
    build_wildfire_input_from_context,
    write_json,
)


def load_monitored_areas(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def determine_response_priority(area_result: dict) -> str:
    severity = area_result.get("severity")
    hotspot_count = int(area_result.get("hotspot_count") or 0)
    nearest_distance = area_result.get("nearest_hotspot_distance_km")
    recurrence_context = area_result.get("recurrence_context") or {}
    recurrence_score = (
        recurrence_context.get("recurrence_score") or 0
        if is_confirmed_gistda_recurrence(recurrence_context)
        else 0
    )

    if severity in {"HIGH", "CRITICAL"} or hotspot_count >= 3:
        return "URGENT_COORDINATION"
    if (
        severity == "MEDIUM"
        and (hotspot_count > 0 or nearest_distance is not None or recurrence_score >= 0.18)
    ):
        return "FIELD_VERIFICATION"
    if severity in {"MEDIUM", "WATCH"} or recurrence_score >= 0.10:
        return "WATCHLIST"
    return "ROUTINE_MONITORING"


def build_explainable_ranking_th(area_result: dict) -> str:
    rank = area_result.get("rank", "--")
    hotspot_count = int(area_result.get("hotspot_count") or 0)
    nearest_distance = area_result.get("nearest_hotspot_distance_km")
    landuse_types = area_result.get("landuse_types") or []
    recurrence_context = area_result.get("recurrence_context") or {}
    recurrence_score = (
        recurrence_context.get("recurrence_score") or 0
        if is_confirmed_gistda_recurrence(recurrence_context)
        else 0
    )

    reasons = []
    if hotspot_count > 0:
        reasons.append(f"พบจุดความร้อน {hotspot_count} จุด")
    else:
        reasons.append("ยังไม่พบจุดความร้อนในรัศมีเฝ้าระวัง")

    if nearest_distance is not None:
        reasons.append(f"จุดที่ใกล้ที่สุดอยู่ห่าง {float(nearest_distance):.2f} กม.")

    if landuse_types:
        reasons.append(f"อยู่ในประเภทพื้นที่ {', '.join(landuse_types[:2])}")

    if recurrence_score > 0:
        reasons.append(f"มีคะแนนประวัติซ้ำซาก {recurrence_score:.2f}")

    return f"พื้นที่นี้อยู่ลำดับที่ {rank} เนื่องจาก" + " ".join(reasons)


def build_province_summary(ranked_areas: list[dict]) -> list[dict]:
    summaries = {}
    for area in ranked_areas:
        province = area.get("province") or "ไม่ทราบจังหวัด"
        summary = summaries.setdefault(
            province,
            {
                "province": province,
                "total_areas": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "total_hotspots": 0,
                "highest_rank_area": None,
                "highest_priority_score": None,
                "province_priority_level": "LOW",
            },
        )
        summary["total_areas"] += 1
        summary["total_hotspots"] += int(area.get("hotspot_count") or 0)
        severity = area.get("severity")
        if severity in {"HIGH", "CRITICAL"}:
            summary["high_count"] += 1
        elif severity in {"MEDIUM", "WATCH"}:
            summary["medium_count"] += 1
        else:
            summary["low_count"] += 1

        if summary["highest_rank_area"] is None or area.get("rank", 9999) < summary["highest_rank_area"].get("rank", 9999):
            summary["highest_rank_area"] = {
                "rank": area.get("rank"),
                "area_id": area.get("area_id"),
                "area_name": area.get("area_name"),
                "priority_score": area.get("priority_score"),
                "severity": area.get("severity"),
            }
            summary["highest_priority_score"] = area.get("priority_score")

    for summary in summaries.values():
        if summary["high_count"] > 0:
            summary["province_priority_level"] = "HIGH"
        elif summary["medium_count"] > 0:
            summary["province_priority_level"] = "MEDIUM"
        else:
            summary["province_priority_level"] = "LOW"

    return sorted(
        summaries.values(),
        key=lambda item: (
            {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(item["province_priority_level"], 3),
            item["highest_rank_area"]["rank"] if item["highest_rank_area"] else 9999,
        ),
    )


def _has_recurrence_or_status_warning(area: dict) -> bool:
    recurrence = area.get("recurrence_context") or {}
    return recurrence.get("status") in {"ok", "not_configured", "error"}


def action_queue_group_for_area(area: dict) -> str:
    severity = area.get("severity")
    hotspot_count = int(area.get("hotspot_count") or 0)

    if severity in {"HIGH", "CRITICAL"}:
        return "urgent_coordination"
    if severity in {"MEDIUM", "WATCH"} and hotspot_count > 0:
        return "field_verification"
    if severity in {"LOW", "MONITOR"} and (hotspot_count > 0 or _has_recurrence_or_status_warning(area)):
        return "close_monitoring"
    return "routine_monitoring"


def build_action_reason_th(area: dict) -> str:
    severity = area.get("severity")
    hotspot_count = int(area.get("hotspot_count") or 0)
    recurrence_status = (area.get("recurrence_context") or {}).get("status")

    if severity in {"HIGH", "CRITICAL"}:
        return "ระดับความเสี่ยงสูง ต้องเร่งประสานงาน"
    if severity in {"MEDIUM", "WATCH"} and hotspot_count > 0:
        return f"พบจุดความร้อน {hotspot_count} จุด ควรตรวจสอบภาคสนาม"
    if severity in {"LOW", "MONITOR"} and hotspot_count > 0:
        return f"ระดับความเสี่ยงต่ำแต่พบจุดความร้อน {hotspot_count} จุด"
    if recurrence_status == "ok":
        return "มีข้อมูลประวัติซ้ำซากจาก GISTDA ควรเฝ้าระวังใกล้ชิด"
    if recurrence_status in {"not_configured", "error"}:
        return "ข้อมูลประวัติซ้ำซากจาก GISTDA ยังไม่สมบูรณ์ ควรติดตามสถานะ"
    return "ยังไม่พบจุดความร้อนในรัศมีเฝ้าระวัง"


def build_action_queue(ranked_areas: list[dict]) -> dict[str, list[dict]]:
    queue: dict[str, list[dict]] = {
        "urgent_coordination": [],
        "field_verification": [],
        "close_monitoring": [],
        "routine_monitoring": [],
    }

    for area in ranked_areas:
        group = action_queue_group_for_area(area)
        queue[group].append(
            {
                "rank": area.get("rank"),
                "area_id": area.get("area_id"),
                "area_name": area.get("area_name"),
                "province": area.get("province"),
                "district": area.get("district"),
                "hotspot_count": int(area.get("hotspot_count") or 0),
                "severity": area.get("severity"),
                "priority_score": area.get("priority_score"),
                "reason_th": build_action_reason_th(area),
                "explainable_ranking_th": area.get("explainable_ranking_th"),
            }
        )

    return queue


def build_ranked_area_result(
    area: dict,
    connector_output: dict,
    environmental_context: dict | None = None,
    recurrence_context: dict | None = None,
) -> dict:
    summary = connector_output.get("summary", {})
    recurrence_context = normalize_gistda_recurrence_response(recurrence_context)
    scoring_payload = build_wildfire_input_from_context(
        connector_output,
        area_id=area["area_id"],
    )
    scored = score_incident(IncidentScoreRequest(**scoring_payload))
    sample = (summary.get("raw_limited_sample") or [{}])[0]

    priority_score = scored.priority_score
    risk_drivers = list(scored.risk_drivers)
    matched_patterns = [pattern.model_dump() for pattern in scored.matched_patterns]
    if is_confirmed_gistda_recurrence(recurrence_context):
        priority_score = _clamp(priority_score + ((recurrence_context.get("recurrence_score") or 0) * 0.2))
        risk_drivers.append("พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA")
        matched_patterns.append(
            {
                "pattern_code": "RECURRENT_RISK_AREA",
                "pattern_name": "Recurrent GISTDA risk area",
                "severity_hint": "MEDIUM",
                "explanation": "GISTDA recurring disaster data indicates repeated historical risk records for this monitored area.",
                "recommended_operational_focus": "Use recurrence evidence to support review prioritization.",
            }
        )

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
        "priority_score": priority_score,
        "severity": scored.severity,
        "recommended_action": scored.recommended_action,
        "operator_summary": scored.operator_summary,
        "risk_drivers": risk_drivers,
        "matched_patterns": matched_patterns,
        "environmental_context": {},
        "environmental_risk_summary": {},
        "recurrence_context": recurrence_context,
    }


def refresh_forest_priority_ranking(
    config_path: Path,
    ranking_path: Path,
    environmental_context_path: Path | None = None,
    recurrence_context_path: Path | None = None,
) -> dict:
    configured = load_monitored_areas(config_path)
    ranked_areas = []

    for area in configured.get("areas", []):
        connector_output = fetch_hotspot_near_point(
            lon=area["lon"],
            lat=area["lat"],
            radius=area.get("radius", 1000.5),
        )
        recurrence_context = get_recurrence_context_for_area(area)
        ranked_areas.append(
            build_ranked_area_result(
                area,
                connector_output,
                {},
                recurrence_context,
            )
        )

    ranked_areas.sort(key=lambda item: item["priority_score"], reverse=True)
    for index, item in enumerate(ranked_areas, start=1):
        item["rank"] = index
        item["response_priority"] = determine_response_priority(item)
        item["explainable_ranking_th"] = build_explainable_ranking_th(item)

    payload = {
        "status": "ok",
        "message": "Forest priority ranking refreshed.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "areas": ranked_areas,
        "province_summary": build_province_summary(ranked_areas),
        "action_queue": build_action_queue(ranked_areas),
    }
    write_json(ranking_path, payload)
    return payload
