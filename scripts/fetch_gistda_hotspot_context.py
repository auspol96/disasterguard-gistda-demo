import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.connectors.gistda_hotspot_api import fetch_hotspot_near_point

LIVE_CONTEXT_PATH = ROOT / "live_context" / "gistda_hotspot_context.json"
GENERATED_INPUT_PATH = ROOT / "sample_inputs" / "gistda_wildfire_haze_chiangmai.json"

CHIANG_MAI_POINT = {"lon": 99.01361, "lat": 19.57651, "radius": 1000.5}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def build_wildfire_input_from_context(
    connector_output: dict,
    area_id: str = "NTH-CHIANGMAI-GISTDA-001",
) -> dict:
    summary = connector_output.get("summary", {})
    hotspot_count = int(summary.get("hotspot_count") or 0)
    nearest_distance = summary.get("nearest_hotspot_distance_km")
    landuse_types = summary.get("landuse_types") or []
    raw_sample = summary.get("raw_limited_sample") or []
    max_frequency = max(
        [int(item.get("frequency") or 0) for item in raw_sample] or [0]
    )

    hotspot_signal = clamp(min(hotspot_count, 10) / 10)
    frequency_signal = clamp(min(max_frequency, 5) / 5)
    distance_signal = 0.0
    if isinstance(nearest_distance, (int, float)):
        distance_signal = clamp(1 - min(float(nearest_distance), 25) / 25)
    landuse_signal = 0.2 if landuse_types else 0.0
    confirmed_clear_radius = (
        connector_output.get("status") == "ok"
        and hotspot_count == 0
        and not landuse_types
        and nearest_distance is None
    )

    if confirmed_clear_radius:
        hazard_score = 0.10
        exposure_score = 0.20
        urgency_score = 0.10
        confidence = 0.25
    elif connector_output.get("status") == "ok":
        hazard_score = clamp(0.45 + hotspot_signal * 0.3 + frequency_signal * 0.15)
        exposure_score = clamp(0.55 + landuse_signal)
        urgency_score = clamp(0.45 + distance_signal * 0.35 + hotspot_signal * 0.1)
        confidence = clamp(0.55 + min(hotspot_count, 3) * 0.07)
    else:
        hazard_score = 0.35
        exposure_score = 0.5
        urgency_score = 0.35
        confidence = 0.25

    risk_drivers = ["GISTDA hotspot API context"]
    if confirmed_clear_radius:
        risk_drivers.append("GISTDA checked, no hotspot detected in monitored radius")
    elif hotspot_count:
        risk_drivers.append(f"{hotspot_count} hotspot record(s) returned")
    if landuse_types:
        risk_drivers.append(f"landuse: {', '.join(landuse_types[:3])}")
    if isinstance(nearest_distance, (int, float)):
        risk_drivers.append(f"nearest hotspot distance {nearest_distance:.2f} km")
    if connector_output.get("status") != "ok":
        risk_drivers.append("live hotspot context not configured")

    return {
        "area_id": area_id,
        "incident_type": "wildfire_haze",
        "hazard_score": hazard_score,
        "exposure_score": exposure_score,
        "urgency_score": urgency_score,
        "confidence": confidence,
        "risk_drivers": risk_drivers,
        "hotspot_count": hotspot_count,
        "landuse_types": landuse_types,
        "nearest_hotspot_distance_km": nearest_distance,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def refresh_hotspot_context() -> dict:
    connector_output = fetch_hotspot_near_point(**CHIANG_MAI_POINT)
    write_json(LIVE_CONTEXT_PATH, connector_output)
    generated_input = build_wildfire_input_from_context(connector_output)
    write_json(GENERATED_INPUT_PATH, generated_input)
    status = connector_output.get("status") or "error"

    if status == "ok":
        message = "GISTDA hotspot context refreshed."
    elif status == "not_configured":
        message = "GISTDA_API_KEY environment variable is not configured."
    else:
        message = connector_output.get("message") or "GISTDA hotspot refresh failed."

    return {
        "status": status,
        "message": message,
        "context_path": _display_path(LIVE_CONTEXT_PATH),
        "generated_input_path": _display_path(GENERATED_INPUT_PATH),
        "summary": connector_output.get("summary", {}),
    }


def main() -> dict:
    return refresh_hotspot_context()


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
