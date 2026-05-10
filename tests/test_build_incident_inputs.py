import json
from pathlib import Path

from app.models import IncidentScoreRequest
from scripts.build_incident_inputs import build_incident_inputs


def test_build_incident_inputs_generates_schema_valid_payloads():
    generated = build_incident_inputs()

    assert set(generated) == {
        "generated_wildfire_haze_chiangmai.json",
        "generated_rapid_flood_chiangrai.json",
        "generated_landslide_maehongson.json",
    }

    for filename, payload in generated.items():
        IncidentScoreRequest(**payload)
        written = json.loads(Path("sample_inputs", filename).read_text())
        assert written == payload
