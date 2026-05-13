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


def _has_value(value: Any) -> bool:
    return value is not None


def _source_label(source: str | None) -> str:
    if source == "open-meteo":
        return "Live Open-Meteo"
    if source == "sample":
        return "Sample fallback"
    return "Unavailable environmental source"


def build_environmental_risk_summary(environmental_context: dict[str, Any]) -> dict[str, Any]:
    temperature = environmental_context.get("temperature_c")
    humidity = environmental_context.get("humidity_percent")
    wind_speed = environmental_context.get("wind_speed_kph")
    rain_probability = environmental_context.get("rain_probability_percent")
    pm25 = environmental_context.get("pm25_ugm3")

    high_fire_spread = (
        _has_value(humidity)
        and _has_value(temperature)
        and _has_value(wind_speed)
        and humidity < 35
        and temperature >= 32
        and wind_speed >= 10
    )
    moderate_fire_signals = [
        _has_value(humidity) and humidity < 45,
        _has_value(temperature) and temperature >= 30,
        _has_value(wind_speed) and wind_speed >= 10,
        _has_value(rain_probability) and rain_probability < 20,
    ]

    if high_fire_spread:
        fire_spread_risk = "HIGH"
    elif sum(bool(signal) for signal in moderate_fire_signals) >= 2:
        fire_spread_risk = "MODERATE"
    else:
        fire_spread_risk = "LOW"

    if _has_value(pm25) and pm25 >= 50:
        haze_health_risk = "HIGH"
    elif _has_value(pm25) and pm25 >= 25:
        haze_health_risk = "MODERATE"
    else:
        haze_health_risk = "LOW"

    weather_supports_escalation = (
        fire_spread_risk == "HIGH"
        or haze_health_risk == "HIGH"
        or (fire_spread_risk == "MODERATE" and haze_health_risk == "MODERATE")
    )
    source_label = _source_label(environmental_context.get("source"))
    summary = (
        f"{source_label} indicates {fire_spread_risk.lower()} fire spread risk "
        f"and {haze_health_risk.lower()} haze health risk."
    )
    if weather_supports_escalation:
        summary += " Weather and air-quality conditions support earlier review or response coordination."
    else:
        summary += " Conditions support continued monitoring unless hotspot evidence changes."

    return {
        "fire_spread_risk": fire_spread_risk,
        "haze_health_risk": haze_health_risk,
        "weather_supports_escalation": weather_supports_escalation,
        "summary": summary,
    }
