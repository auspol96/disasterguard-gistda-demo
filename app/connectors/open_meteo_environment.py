from datetime import datetime, timezone
from typing import Any

import requests

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
DEFAULT_TIMEOUT_SECONDS = 8


def wind_degrees_to_compass(degrees: float | int | None) -> str | None:
    if degrees is None:
        return None
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round((float(degrees) % 360) / 45) % 8
    return directions[index]


def _current_value(payload: dict[str, Any], key: str) -> Any:
    return (payload.get("current") or {}).get(key)


def _first_hourly_value(payload: dict[str, Any], key: str) -> Any:
    values = (payload.get("hourly") or {}).get(key) or []
    return values[0] if values else None


def fetch_open_meteo_environment(lat: float, lon: float) -> dict[str, Any]:
    try:
        forecast_response = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
                "hourly": "precipitation_probability",
                "forecast_hours": 1,
                "timezone": "auto",
            },
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        forecast_response.raise_for_status()
        forecast = forecast_response.json()

        air_quality_response = requests.get(
            AIR_QUALITY_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "pm2_5",
                "timezone": "auto",
            },
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
        air_quality_response.raise_for_status()
        air_quality = air_quality_response.json()
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}
    except ValueError as exc:
        return {"status": "error", "message": f"Invalid Open-Meteo JSON response: {exc}"}

    wind_direction_degrees = _current_value(forecast, "wind_direction_10m")
    return {
        "source": "open-meteo",
        "temperature_c": _current_value(forecast, "temperature_2m"),
        "humidity_percent": _current_value(forecast, "relative_humidity_2m"),
        "wind_speed_kph": _current_value(forecast, "wind_speed_10m"),
        "wind_direction": wind_degrees_to_compass(wind_direction_degrees),
        "wind_direction_degrees": wind_direction_degrees,
        "rain_probability_percent": _first_hourly_value(forecast, "precipitation_probability"),
        "pm25_ugm3": _current_value(air_quality, "pm2_5"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
    }
