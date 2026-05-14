from datetime import datetime, timezone
from typing import Any


def _count_hotspot_areas(areas: list[dict[str, Any]]) -> int:
    return sum(1 for area in areas if int(area.get("hotspot_count") or 0) > 0)


def _count_by_severity(areas: list[dict[str, Any]], severities: set[str]) -> int:
    return sum(1 for area in areas if area.get("severity") in severities)


def _queue_count(action_queue: dict[str, list[dict[str, Any]]], key: str) -> int:
    return len(action_queue.get(key) or [])


def build_key_numbers(ranking: dict[str, Any]) -> dict[str, int]:
    areas = ranking.get("areas", [])
    action_queue = ranking.get("action_queue", {})
    return {
        "total_areas": len(areas),
        "hotspot_area_count": _count_hotspot_areas(areas),
        "total_hotspots": sum(int(area.get("hotspot_count") or 0) for area in areas),
        "high_count": _count_by_severity(areas, {"HIGH", "CRITICAL"}),
        "medium_count": _count_by_severity(areas, {"MEDIUM", "WATCH"}),
        "low_count": _count_by_severity(areas, {"LOW", "MONITOR"}),
        "provinces_monitored": len({area.get("province") for area in areas if area.get("province")}),
        "urgent_queue_count": _queue_count(action_queue, "urgent_coordination"),
        "field_verification_count": _queue_count(action_queue, "field_verification"),
    }


def build_top_priority_areas(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    areas = sorted(ranking.get("areas", []), key=lambda area: int(area.get("rank") or 9999))
    return [
        {
            "rank": area.get("rank"),
            "area_name": area.get("area_name"),
            "province": area.get("province"),
            "district": area.get("district"),
            "hotspot_count": int(area.get("hotspot_count") or 0),
            "severity": area.get("severity"),
            "priority_score": area.get("priority_score"),
            "reason_th": area.get("explainable_ranking_th"),
            "recommended_action": area.get("recommended_action"),
        }
        for area in areas[:5]
    ]


def build_province_attention_summary(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    province_summary = ranking.get("province_summary", [])
    return [
        {
            "province": item.get("province"),
            "province_priority_level": item.get("province_priority_level"),
            "total_areas": item.get("total_areas"),
            "total_hotspots": item.get("total_hotspots"),
            "high_count": item.get("high_count", 0) + item.get("critical_count", 0),
            "medium_count": item.get("medium_count"),
            "highest_rank_area": item.get("highest_rank_area"),
            "summary_th": (
                f"{item.get('province')} มีจุดความร้อนรวม {item.get('total_hotspots', 0)} จุด "
                f"และพื้นที่อันดับสูงสุดคือ {((item.get('highest_rank_area') or {}).get('area_name') or '--')}"
            ),
        }
        for item in province_summary
    ]


def build_action_queue_summary(ranking: dict[str, Any]) -> dict[str, dict[str, Any]]:
    action_queue = ranking.get("action_queue", {})
    labels = {
        "urgent_coordination": "เร่งประสานงาน",
        "field_verification": "ตรวจสอบภาคสนาม",
        "close_monitoring": "เฝ้าระวังใกล้ชิด",
        "routine_monitoring": "เฝ้าระวังตามปกติ",
    }
    return {
        key: {
            "label_th": label,
            "count": len(action_queue.get(key) or []),
            "top_items": (action_queue.get(key) or [])[:5],
        }
        for key, label in labels.items()
    }


def build_change_summary_th(ranking: dict[str, Any]) -> str:
    change_summary = ranking.get("change_summary") or {}
    if change_summary.get("status") == "no_previous":
        return "ยังไม่มีข้อมูลรอบก่อนหน้าเพื่อเปรียบเทียบ"

    new_hotspot = len(change_summary.get("new_hotspot_areas") or [])
    increased_hotspot = len(change_summary.get("increased_hotspot_areas") or [])
    severity_increased = len(change_summary.get("severity_increased_areas") or [])
    rank_improved = len(change_summary.get("rank_improved_areas") or [])
    unchanged_high = len(change_summary.get("unchanged_high_priority_areas") or [])
    return (
        f"เทียบกับรอบก่อนหน้า พบพื้นที่จุดความร้อนใหม่ {new_hotspot} พื้นที่ "
        f"จุดความร้อนเพิ่มขึ้น {increased_hotspot} พื้นที่ "
        f"ระดับความเสี่ยงเพิ่มขึ้น {severity_increased} พื้นที่ "
        f"อันดับความเสี่ยงสูงขึ้น {rank_improved} พื้นที่ "
        f"และพื้นที่เสี่ยงสูงที่ยังต้องติดตาม {unchanged_high} พื้นที่"
    )


def build_executive_summary_th(ranking: dict[str, Any], key_numbers: dict[str, int]) -> str:
    top_areas = build_top_priority_areas(ranking)[:2]
    top_names = "และ".join([area.get("area_name") or "--" for area in top_areas]) or "--"
    return (
        f"ภาพรวมล่าสุดพบพื้นที่เฝ้าระวัง {key_numbers['total_areas']} พื้นที่ "
        f"มีพื้นที่พบจุดความร้อน {key_numbers['hotspot_area_count']} พื้นที่ "
        f"จุดความร้อนรวม {key_numbers['total_hotspots']} จุด "
        f"โดยพื้นที่ที่ควรเร่งติดตามคือ{top_names} เนื่องจากอยู่ในลำดับความเสี่ยงสูงสุดของระบบ"
    )


def build_data_source_status(ranking: dict[str, Any]) -> dict[str, Any]:
    recurrence_statuses = sorted(
        {
            (area.get("recurrence_context") or {}).get("status")
            for area in ranking.get("areas", [])
            if (area.get("recurrence_context") or {}).get("status")
        }
    )
    return {
        "gistda_hotspot_data_status": ranking.get("status", "unknown"),
        "gistda_recurrence_data_status": ", ".join(recurrence_statuses) if recurrence_statuses else "not_available",
        "last_refreshed_at": ranking.get("generated_at"),
        "mock_or_sample_disaster_data_used": False,
        "message_th": "ใช้ข้อมูลหลักฐานภัยพิบัติจาก GISTDA Hotspot API และ GISTDA Recurring Disaster API เท่านั้น ไม่ใช้ข้อมูลภัยพิบัติจำลอง",
    }


def build_recommended_next_actions(ranking: dict[str, Any]) -> list[str]:
    action_queue = ranking.get("action_queue", {})
    change_summary = ranking.get("change_summary") or {}
    actions = []
    if action_queue.get("urgent_coordination"):
        actions.append("ประสานหน่วยงานพื้นที่เพื่อตรวจสอบพื้นที่เสี่ยงสูง")
    if action_queue.get("field_verification"):
        actions.append("ติดตามพื้นที่ที่พบจุดความร้อนหลายจุด")
    if change_summary.get("severity_increased_areas"):
        actions.append("ตรวจสอบพื้นที่ที่ระดับความเสี่ยงเพิ่มขึ้นจากรอบก่อนหน้า")
    if change_summary.get("new_hotspot_areas"):
        actions.append("ตรวจสอบพื้นที่ที่พบจุดความร้อนใหม่")
    if not actions:
        actions.append("ติดตามข้อมูล GISTDA รอบถัดไปและคงการเฝ้าระวังตามปกติ")
    return actions


def build_daily_briefing(ranking: dict[str, Any]) -> dict[str, Any]:
    key_numbers = build_key_numbers(ranking)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title_th": "รายงานสถานการณ์ประจำวัน ForestGuard North Thailand",
        "executive_summary_th": build_executive_summary_th(ranking, key_numbers),
        "key_numbers": key_numbers,
        "top_priority_areas": build_top_priority_areas(ranking),
        "province_attention_summary": build_province_attention_summary(ranking),
        "action_queue_summary": build_action_queue_summary(ranking),
        "change_summary_th": build_change_summary_th(ranking),
        "data_source_status": build_data_source_status(ranking),
        "recommended_next_actions": build_recommended_next_actions(ranking),
    }
