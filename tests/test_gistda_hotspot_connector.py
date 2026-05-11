import json
from pathlib import Path

from app.connectors.gistda_hotspot_api import (
    fetch_hotspot_near_point,
    summarize_hotspot_response,
)
from app.models import IncidentScoreRequest
from scripts import fetch_gistda_hotspot_context


EXAMPLE_RESPONSE = {
    "terra": [{"date": "2022-03-28", "data": []}],
    "aqua": [{"date": "2022-03-28", "data": []}],
    "suomi-npp": [
        {
            "date": "2022-03-28",
            "data": [
                {
                    "code": 1,
                    "landuse": "forest",
                    "frequency": 1,
                    "data": [
                        {
                            "lat": "19.57651",
                            "lon": "99.01361",
                            "pv_tn": "Chiang Mai",
                            "ap_tn": "Demo District",
                            "tb_tn": "Demo Subdistrict",
                            "village": "Demo Village",
                            "distance": 5.82881,
                            "direction": "S",
                        }
                    ],
                }
            ],
        }
    ],
}


def test_fetch_hotspot_near_point_returns_not_configured_without_key(monkeypatch):
    monkeypatch.delenv("GISTDA_API_KEY", raising=False)

    result = fetch_hotspot_near_point(lon=99.01361, lat=19.57651)

    assert result["status"] == "not_configured"
    assert result["summary"]["status"] == "not_configured"
    assert result["summary"]["hotspot_count"] == 0


def test_summarize_hotspot_response_extracts_example_fields():
    summary = summarize_hotspot_response(EXAMPLE_RESPONSE)

    assert summary["status"] == "ok"
    assert summary["source_satellites_checked"] == ["terra", "aqua", "suomi-npp"]
    assert summary["hotspot_count"] == 1
    assert summary["dates_available"] == ["2022-03-28"]
    assert summary["nearest_hotspot_distance_km"] == 5.82881
    assert summary["provinces_detected"] == ["Chiang Mai"]
    assert summary["landuse_types"] == ["forest"]
    assert summary["raw_limited_sample"][0]["direction"] == "S"


def test_fetch_script_without_key_writes_context_and_schema_valid_input(monkeypatch):
    monkeypatch.delenv("GISTDA_API_KEY", raising=False)

    result = fetch_gistda_hotspot_context.main()

    assert result["status"] == "not_configured"
    context = json.loads(Path("live_context/gistda_hotspot_context.json").read_text())
    assert context["status"] == "not_configured"

    generated = json.loads(
        Path("sample_inputs/gistda_wildfire_haze_chiangmai.json").read_text()
    )
    IncidentScoreRequest(**generated)
