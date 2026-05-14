from typing import Any

from app.connectors.gistda_recurring_api import fetch_gistda_recurrence_context

NO_DATA_MESSAGE = "ยังไม่พบข้อมูลประวัติความเสี่ยงซ้ำซากจาก GISTDA สำหรับพื้นที่นี้"
NOT_CONFIGURED_MESSAGE = "ยังไม่ได้ตั้งค่า GISTDA_API_KEY สำหรับดึงข้อมูลประวัติซ้ำซาก"
ERROR_MESSAGE = "ไม่สามารถดึงข้อมูลประวัติซ้ำซากจาก GISTDA ได้ในขณะนี้"


def calculate_recurrence_score(
    hotspot_recurrence_count: int,
    flood_recurrence_count: int,
    drought_recurrence_count: int,
) -> float:
    weighted = (
        hotspot_recurrence_count * 0.045
        + flood_recurrence_count * 0.025
        + drought_recurrence_count * 0.025
    )
    return round(max(0.0, min(0.3, weighted)), 2)


def _record_type(record: dict[str, Any]) -> str:
    value = (
        record.get("disaster_type")
        or record.get("type")
        or record.get("hazard_type")
        or record.get("incident_type")
        or record.get("category")
        or ""
    )
    return str(value).lower()


def _count_records(records: list[dict[str, Any]], keywords: tuple[str, ...]) -> int:
    count = 0
    for record in records:
        text = _record_type(record)
        if any(keyword in text for keyword in keywords):
            count += 1
    return count


def normalize_gistda_recurrence_response(response: dict[str, Any] | None) -> dict[str, Any]:
    response = response or {}
    source = response.get("source") or "gistda_recurring_api"
    status = response.get("status") or "error"

    if status == "not_configured":
        return {
            "source": source,
            "status": "not_configured",
            "recurrence_score": None,
            "raw_limited_sample": [],
            "fetched_at": response.get("fetched_at"),
            "recurrence_summary_th": NOT_CONFIGURED_MESSAGE,
        }

    if status == "error":
        return {
            "source": source,
            "status": "error",
            "recurrence_score": None,
            "raw_limited_sample": [],
            "fetched_at": response.get("fetched_at"),
            "recurrence_summary_th": ERROR_MESSAGE,
        }

    records = response.get("records") or []
    if status != "ok" or not records:
        return {
            "source": source,
            "status": "not_found",
            "recurrence_score": None,
            "raw_limited_sample": response.get("raw_limited_sample") or [],
            "fetched_at": response.get("fetched_at"),
            "recurrence_summary_th": NO_DATA_MESSAGE,
        }

    hotspot_count = _count_records(records, ("hotspot", "wildfire", "fire", "ไฟ", "จุดความร้อน"))
    flood_count = _count_records(records, ("flood", "น้ำท่วม", "อุทก"))
    drought_count = _count_records(records, ("drought", "แล้ง", "ภัยแล้ง"))

    explicit_hotspot_count = response.get("hotspot_recurrence_count")
    explicit_flood_count = response.get("flood_recurrence_count")
    explicit_drought_count = response.get("drought_recurrence_count")
    if explicit_hotspot_count is not None:
        hotspot_count = int(explicit_hotspot_count)
    if explicit_flood_count is not None:
        flood_count = int(explicit_flood_count)
    if explicit_drought_count is not None:
        drought_count = int(explicit_drought_count)

    score = calculate_recurrence_score(hotspot_count, flood_count, drought_count)
    return {
        "source": source,
        "status": "ok",
        "hotspot_recurrence_count": hotspot_count,
        "flood_recurrence_count": flood_count,
        "drought_recurrence_count": drought_count,
        "recurrence_score": score,
        "raw_limited_sample": response.get("raw_limited_sample") or records[:5],
        "fetched_at": response.get("fetched_at"),
        "recurrence_summary_th": (
            f"พบข้อมูลประวัติซ้ำซากจาก GISTDA: จุดความร้อน {hotspot_count} ครั้ง "
            f"น้ำท่วม {flood_count} ครั้ง และแล้ง {drought_count} ครั้ง"
        ),
    }


def get_recurrence_context_for_area(area: dict[str, Any]) -> dict[str, Any]:
    response = fetch_gistda_recurrence_context(
        lat=area["lat"],
        lon=area["lon"],
        radius=area.get("radius", 5000),
        province=area.get("province"),
        district=area.get("district"),
        area_id=area.get("area_id"),
    )
    return normalize_gistda_recurrence_response(response)


def is_confirmed_gistda_recurrence(context: dict[str, Any] | None) -> bool:
    context = context or {}
    return (
        context.get("status") == "ok"
        and context.get("source") in {"gistda_recurring_api", "gistda_recurring_v2_api"}
        and context.get("recurrence_score") is not None
    )
