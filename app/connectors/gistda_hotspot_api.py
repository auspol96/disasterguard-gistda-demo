import os
from typing import Any

GISTDA_HOTSPOT_URL = "https://api.sphere.gistda.or.th/services/info/disaster-hotspot"
DEFAULT_TIMEOUT_SECONDS = 10


def _flatten_hotspot_records(response: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for satellite, date_groups in response.items():
        if not isinstance(date_groups, list):
            continue
        for date_group in date_groups:
            if not isinstance(date_group, dict):
                continue
            date = date_group.get("date")
            for group in date_group.get("data") or []:
                if not isinstance(group, dict):
                    continue
                for hotspot in group.get("data") or []:
                    if not isinstance(hotspot, dict):
                        continue
                    records.append(
                        {
                            "satellite": satellite,
                            "date": date,
                            "landuse": group.get("landuse"),
                            "frequency": group.get("frequency"),
                            "hotspot": hotspot,
                        }
                    )
    return records


def _unique_sorted(values: list[Any]) -> list[Any]:
    return sorted({value for value in values if value not in (None, "")})


def summarize_hotspot_response(response: dict[str, Any]) -> dict[str, Any]:
    records = _flatten_hotspot_records(response)
    distances = [
        float(record["hotspot"]["distance"])
        for record in records
        if record.get("hotspot", {}).get("distance") not in (None, "")
    ]

    raw_limited_sample = []
    for record in records[:3]:
        hotspot = record["hotspot"]
        raw_limited_sample.append(
            {
                "satellite": record["satellite"],
                "date": record["date"],
                "landuse": record["landuse"],
                "frequency": record["frequency"],
                "lat": hotspot.get("lat"),
                "lon": hotspot.get("lon"),
                "province": hotspot.get("pv_tn"),
                "district": hotspot.get("ap_tn"),
                "subdistrict": hotspot.get("tb_tn"),
                "village": hotspot.get("village"),
                "distance": hotspot.get("distance"),
                "direction": hotspot.get("direction"),
            }
        )

    return {
        "status": "ok",
        "source_satellites_checked": list(response.keys()),
        "hotspot_count": len(records),
        "dates_available": _unique_sorted(
            [
                date_group.get("date")
                for date_groups in response.values()
                if isinstance(date_groups, list)
                for date_group in date_groups
                if isinstance(date_group, dict)
            ]
        ),
        "nearest_hotspot_distance_km": min(distances) if distances else None,
        "provinces_detected": _unique_sorted(
            [record["hotspot"].get("pv_tn") for record in records]
        ),
        "landuse_types": _unique_sorted([record.get("landuse") for record in records]),
        "raw_limited_sample": raw_limited_sample,
    }


def fetch_hotspot_near_point(lon: float, lat: float, radius: float = 1000.5) -> dict[str, Any]:
    api_key = os.getenv("GISTDA_API_KEY")
    if not api_key:
        return {
            "status": "not_configured",
            "message": "GISTDA_API_KEY environment variable is not configured.",
            "summary": {
                "status": "not_configured",
                "source_satellites_checked": [],
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
                "raw_limited_sample": [],
            },
        }

    params = {"lon": lon, "lat": lat, "radius": radius, "key": api_key}
    try:
        import requests
    except ImportError as exc:
        return {
            "status": "error",
            "message": f"requests dependency is not installed: {exc}",
            "summary": {
                "status": "error",
                "source_satellites_checked": [],
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
                "raw_limited_sample": [],
            },
        }

    try:
        response = requests.get(
            GISTDA_HOTSPOT_URL,
            params=params,
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException as exc:
        return {
            "status": "error",
            "message": str(exc),
            "summary": {
                "status": "error",
                "source_satellites_checked": [],
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
                "raw_limited_sample": [],
            },
        }
    except ValueError as exc:
        return {
            "status": "error",
            "message": f"Invalid JSON response: {exc}",
            "summary": {
                "status": "error",
                "source_satellites_checked": [],
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
                "raw_limited_sample": [],
            },
        }

    summary = summarize_hotspot_response(raw)
    return {
        "status": "ok",
        "request": {"lon": lon, "lat": lat, "radius": radius},
        "summary": summary,
        "raw_response": raw,
    }
