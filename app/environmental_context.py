import json
from pathlib import Path
from typing import Any

from app.connectors.open_meteo_environment import fetch_open_meteo_environment


def load_environmental_context_samples(config_path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if "areas" in payload and isinstance(payload["areas"], dict):
        return payload["areas"]
    return payload


def get_sample_environmental_context_for_area(area_id: str, config_path: Path) -> dict[str, Any]:
    sample = dict(load_environmental_context_samples(config_path).get(area_id, {}))
    if sample:
        sample.setdefault("source", "sample")
        sample.setdefault("fetched_at", None)
    return sample


def get_environmental_context_for_area(
    area_id: str,
    config_path: Path,
    lat: float | None = None,
    lon: float | None = None,
) -> dict[str, Any]:
    if lat is not None and lon is not None:
        live_context = fetch_open_meteo_environment(lat, lon)
        if live_context.get("status") == "ok":
            return live_context

    fallback = get_sample_environmental_context_for_area(area_id, config_path)
    if fallback:
        return fallback

    return {}
