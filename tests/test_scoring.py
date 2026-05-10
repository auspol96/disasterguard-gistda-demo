import pytest

from app.models import IncidentScoreRequest
from app.scoring import calculate_priority_score, classify_severity, score_incident


def make_request(**overrides):
    data = {
        "area_id": "NTH-TEST-001",
        "incident_type": "wildfire_haze",
        "hazard_score": 0.82,
        "exposure_score": 0.74,
        "urgency_score": 0.79,
        "confidence": 0.76,
        "risk_drivers": ["recent hotspot cluster", "nearby community exposure"],
    }
    data.update(overrides)
    return IncidentScoreRequest(**data)


def test_priority_score_uses_transparent_weighted_formula():
    request = make_request()

    assert calculate_priority_score(request) == 0.78


@pytest.mark.parametrize(
    ("score", "severity"),
    [
        (0.00, "LOW"),
        (0.34, "LOW"),
        (0.35, "WATCH"),
        (0.54, "WATCH"),
        (0.55, "MEDIUM"),
        (0.74, "MEDIUM"),
        (0.75, "HIGH"),
        (0.89, "HIGH"),
        (0.90, "CRITICAL"),
        (1.00, "CRITICAL"),
    ],
)
def test_severity_boundaries(score, severity):
    assert classify_severity(score) == severity


def test_score_incident_returns_action_summary_and_drivers():
    result = score_incident(make_request())

    assert result.severity == "HIGH"
    assert result.recommended_action == "PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE"
    assert "priority operator review" in result.operator_summary
    assert result.risk_drivers == [
        "recent hotspot cluster",
        "nearby community exposure",
    ]
