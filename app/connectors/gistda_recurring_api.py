import os
from datetime import datetime, timezone
from typing import Any

import requests


DEFAULT_RECURRING_API_URL = "https://api.sphere.gistda.or.th/services/info/disaster-recurring"
DEFAULT_RECURRING_V2_API_URL = "https://api.sphere.gistda.or.th/services/info/disaster-recurring/v2"


def _api_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "X-API-Key": api_key,
    }


def _records_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "items", "features", "records", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return [payload] if payload else []


def fetch_gistda_recurrence_context(
    *,
    lat: float,
    lon: float,
    radius: float,
    province: str | None = None,
    district: str | None = None,
    area_id: str | None = None,
) -> dict[str, Any]:
    api_key = os.getenv("GISTDA_API_KEY")
    if not api_key:
        return {
            "source": "gistda_recurring_api",
            "status": "not_configured",
            "recurrence_summary_th": "ยังไม่ได้ตั้งค่า GISTDA_API_KEY สำหรับดึงข้อมูลประวัติซ้ำซาก",
        }

    api_url = os.getenv("GISTDA_RECURRING_API_URL", DEFAULT_RECURRING_API_URL)
    api_v2_url = os.getenv("GISTDA_RECURRING_V2_API_URL", DEFAULT_RECURRING_V2_API_URL)
    params = {
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "province": province,
        "district": district,
        "area_id": area_id,
        "key": api_key,
    }
    params = {key: value for key, value in params.items() if value is not None}

    last_error = None
    for source, url in (
        ("gistda_recurring_v2_api", api_v2_url),
        ("gistda_recurring_api", api_url),
    ):
        try:
            response = requests.get(
                url,
                params=params,
                headers=_api_headers(api_key),
                timeout=20,
            )
            response.raise_for_status()
            records = _records_from_payload(response.json())
            return {
                "source": source,
                "status": "ok" if records else "not_found",
                "records": records,
                "raw_limited_sample": records[:5],
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            last_error = str(exc)

    return {
        "source": "gistda_recurring_api",
        "status": "error",
        "message": last_error or "GISTDA recurring API request failed.",
        "recurrence_summary_th": "ไม่สามารถดึงข้อมูลประวัติซ้ำซากจาก GISTDA ได้ในขณะนี้",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
