import json
import shutil
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


SEVERITY_ORDER = {
    "LOW": 0,
    "MONITOR": 0,
    "WATCH": 1,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}

NO_PREVIOUS_CHANGE_MESSAGE = "ยังไม่มีข้อมูลรอบก่อนหน้า"
NO_PREVIOUS_COMPARE_MESSAGE = "ยังไม่มีข้อมูลรอบก่อนหน้าเพื่อเปรียบเทียบ"


def previous_ranking_path_for(ranking_path: Path) -> Path:
    return ranking_path.with_name("forest_priority_ranking_previous.json")


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

    return f"พื้นที่นี้อยู่ในลำดับที่ {rank} เนื่องจาก" + " ".join(reasons)


def build_province_summary(ranked_areas: list[dict]) -> list[dict]:
    summaries = {}
    for area in ranked_areas:
        province = area.get("province") or "ไม่ทราบจังหวัด"
        summary = summaries.setdefault(
            province,
            {
                "province": province,
                "total_areas": 0,
                "critical_count": 0,
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
        if severity == "CRITICAL":
            summary["critical_count"] += 1
        elif severity == "HIGH":
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
        if summary["critical_count"] > 0:
            summary["province_priority_level"] = "CRITICAL"
        elif summary["high_count"] > 0:
            summary["province_priority_level"] = "HIGH"
        elif summary["medium_count"] > 0:
            summary["province_priority_level"] = "MEDIUM"
        else:
            summary["province_priority_level"] = "LOW"

    return sorted(
        summaries.values(),
        key=lambda item: (
            {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(item["province_priority_level"], 4),
            item["highest_rank_area"]["rank"] if item["highest_rank_area"] else 9999,
        ),
    )


def action_queue_group_for_area(area: dict) -> str:
    severity = area.get("severity")
    hotspot_count = int(area.get("hotspot_count") or 0)

    if severity in {"CRITICAL", "HIGH"}:
        return "urgent_coordination"
    if severity == "MEDIUM" and hotspot_count > 0:
        return "field_verification"
    if severity == "LOW" and hotspot_count > 0:
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
                "recommended_action": area.get("recommended_action"),
                "short_reason_th": build_action_reason_th(area),
                "explainable_ranking_th": area.get("explainable_ranking_th"),
            }
        )

    return queue


def _area_by_id(payload: dict | None) -> dict[str, dict]:
    if not payload:
        return {}
    return {
        area["area_id"]: area
        for area in payload.get("areas", [])
        if area.get("area_id")
    }


def _severity_value(severity: str | None) -> int:
    return SEVERITY_ORDER.get(severity or "", -1)


def build_change_item(current: dict, previous: dict, reason: str) -> dict:
    return {
        "area_id": current.get("area_id"),
        "area_name": current.get("area_name"),
        "province": current.get("province"),
        "district": current.get("district"),
        "previous_rank": previous.get("rank"),
        "current_rank": current.get("rank"),
        "previous_hotspot_count": int(previous.get("hotspot_count") or 0),
        "current_hotspot_count": int(current.get("hotspot_count") or 0),
        "previous_severity": previous.get("severity"),
        "current_severity": current.get("severity"),
        "change_reason_th": reason,
    }


def build_change_status_th(current: dict, previous: dict | None) -> str:
    if not previous:
        return NO_PREVIOUS_CHANGE_MESSAGE

    previous_rank = previous.get("rank")
    current_rank = current.get("rank")
    previous_hotspots = int(previous.get("hotspot_count") or 0)
    current_hotspots = int(current.get("hotspot_count") or 0)
    previous_severity = previous.get("severity")
    current_severity = current.get("severity")

    if previous_rank is not None and current_rank is not None and int(current_rank) < int(previous_rank):
        return f"อันดับดีขึ้นจาก {previous_rank} เป็น {current_rank}"
    if current_hotspots > previous_hotspots:
        return f"จำนวนจุดความร้อนเพิ่มจาก {previous_hotspots} เป็น {current_hotspots}"
    if _severity_value(current_severity) > _severity_value(previous_severity):
        return f"ระดับความเสี่ยงเพิ่มจาก {previous_severity} เป็น {current_severity}"
    if previous_rank is not None and current_rank is not None and int(current_rank) > int(previous_rank):
        return f"อันดับลดลงจาก {previous_rank} เป็น {current_rank}"
    if current_hotspots < previous_hotspots:
        return f"จำนวนจุดความร้อนลดลงจาก {previous_hotspots} เป็น {current_hotspots}"
    if _severity_value(current_severity) < _severity_value(previous_severity):
        return f"ระดับความเสี่ยงลดลงจาก {previous_severity} เป็น {current_severity}"
    return "ยังไม่พบการเปลี่ยนแปลงสำคัญจากรอบก่อนหน้า"


def build_change_summary(current_payload: dict, previous_payload: dict | None = None) -> dict:
    groups: dict[str, list[dict]] = {
        "new_hotspot_areas": [],
        "increased_hotspot_areas": [],
        "decreased_hotspot_areas": [],
        "severity_increased_areas": [],
        "severity_decreased_areas": [],
        "rank_improved_areas": [],
        "rank_dropped_areas": [],
        "unchanged_high_priority_areas": [],
    }
    if not previous_payload:
        return {
            "status": "no_previous",
            "message": NO_PREVIOUS_COMPARE_MESSAGE,
            **groups,
        }

    previous_by_id = _area_by_id(previous_payload)
    for current in current_payload.get("areas", []):
        previous = previous_by_id.get(current.get("area_id"))
        if not previous:
            continue

        previous_hotspots = int(previous.get("hotspot_count") or 0)
        current_hotspots = int(current.get("hotspot_count") or 0)
        previous_severity = previous.get("severity")
        current_severity = current.get("severity")
        previous_rank = previous.get("rank")
        current_rank = current.get("rank")

        if previous_hotspots == 0 and current_hotspots > 0:
            groups["new_hotspot_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"พบจุดความร้อนใหม่ {current_hotspots} จุด",
                )
            )
        if current_hotspots > previous_hotspots:
            groups["increased_hotspot_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"จำนวนจุดความร้อนเพิ่มจาก {previous_hotspots} เป็น {current_hotspots}",
                )
            )
        if current_hotspots < previous_hotspots:
            groups["decreased_hotspot_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"จำนวนจุดความร้อนลดลงจาก {previous_hotspots} เป็น {current_hotspots}",
                )
            )
        if _severity_value(current_severity) > _severity_value(previous_severity):
            groups["severity_increased_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"ระดับความเสี่ยงเพิ่มจาก {previous_severity} เป็น {current_severity}",
                )
            )
        if _severity_value(current_severity) < _severity_value(previous_severity):
            groups["severity_decreased_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"ระดับความเสี่ยงลดลงจาก {previous_severity} เป็น {current_severity}",
                )
            )
        if previous_rank is not None and current_rank is not None and int(current_rank) < int(previous_rank):
            groups["rank_improved_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"อันดับความเสี่ยงสูงขึ้นจาก {previous_rank} เป็น {current_rank}",
                )
            )
        if previous_rank is not None and current_rank is not None and int(current_rank) > int(previous_rank):
            groups["rank_dropped_areas"].append(
                build_change_item(
                    current,
                    previous,
                    f"อันดับความเสี่ยงลดลงจาก {previous_rank} เป็น {current_rank}",
                )
            )
        if (
            current_severity in {"HIGH", "CRITICAL"}
            and previous_severity == current_severity
            and previous_rank == current_rank
        ):
            groups["unchanged_high_priority_areas"].append(
                build_change_item(
                    current,
                    previous,
                    "พื้นที่เสี่ยงสูงยังคงต้องติดตามต่อเนื่อง",
                )
            )

    return {
        "status": "ok",
        "message": "เปรียบเทียบกับข้อมูลรอบก่อนหน้าแล้ว",
        **groups,
    }


def apply_change_status_to_areas(current_payload: dict, previous_payload: dict | None = None) -> None:
    previous_by_id = _area_by_id(previous_payload)
    for area in current_payload.get("areas", []):
        area["change_status_th"] = build_change_status_th(
            area,
            previous_by_id.get(area.get("area_id")),
        )


def read_ranking_payload(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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
    previous_path = previous_ranking_path_for(ranking_path)
    previous_payload = read_ranking_payload(ranking_path)
    if ranking_path.exists():
        previous_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ranking_path, previous_path)

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
    apply_change_status_to_areas(payload, previous_payload)
    payload["change_summary"] = build_change_summary(payload, previous_payload)
    write_json(ranking_path, payload)
    return payload
