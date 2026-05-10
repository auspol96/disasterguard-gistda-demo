from app.actions import recommended_action_for_severity
from app.config import SCORE_WEIGHTS
from app.models import IncidentScoreRequest, IncidentScoreResponse


def calculate_priority_score(request: IncidentScoreRequest) -> float:
    raw_score = (
        request.hazard_score * SCORE_WEIGHTS["hazard_score"]
        + request.exposure_score * SCORE_WEIGHTS["exposure_score"]
        + request.urgency_score * SCORE_WEIGHTS["urgency_score"]
        + request.confidence * SCORE_WEIGHTS["confidence"]
    )
    return round(raw_score, 2)


def classify_severity(priority_score: float) -> str:
    if priority_score <= 0.34:
        return "LOW"
    if priority_score <= 0.54:
        return "WATCH"
    if priority_score <= 0.74:
        return "MEDIUM"
    if priority_score <= 0.89:
        return "HIGH"
    return "CRITICAL"


def generate_operator_summary(request: IncidentScoreRequest, severity: str) -> str:
    incident_label = request.incident_type.value.replace("_", " ")
    driver_text = ", ".join(request.risk_drivers[:3])

    if severity in {"HIGH", "CRITICAL"}:
        base = (
            f"{request.area_id} should receive priority operator review for "
            f"{incident_label} because hazard, exposure, urgency, and confidence "
            "signals combine into an elevated priority result"
        )
    elif severity == "MEDIUM":
        base = (
            f"{request.area_id} should be reviewed in the next operational cycle "
            f"for {incident_label} because multiple signals indicate meaningful risk"
        )
    elif severity == "WATCH":
        base = (
            f"{request.area_id} should remain in the monitoring queue for "
            f"{incident_label} because current signals are notable but not yet high priority"
        )
    else:
        base = (
            f"{request.area_id} can remain under routine monitoring for "
            f"{incident_label} based on the current transparent scoring inputs"
        )

    if driver_text:
        return f"{base}. Key drivers: {driver_text}."
    return f"{base}."


def score_incident(request: IncidentScoreRequest) -> IncidentScoreResponse:
    priority_score = calculate_priority_score(request)
    severity = classify_severity(priority_score)

    return IncidentScoreResponse(
        area_id=request.area_id,
        incident_type=request.incident_type,
        priority_score=priority_score,
        severity=severity,
        recommended_action=recommended_action_for_severity(severity),
        operator_summary=generate_operator_summary(request, severity),
        risk_drivers=request.risk_drivers,
    )
