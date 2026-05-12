from app.actions import build_operator_summary, classify_severity, recommended_action_for_severity
from app.config import SCORING_WEIGHTS
from app.incident_patterns import match_wildfire_haze_patterns
from app.models import IncidentScoreRequest, IncidentScoreResponse
def calculate_priority_score(request: IncidentScoreRequest) -> float:
    score = (SCORING_WEIGHTS['hazard_score']*request.hazard_score + SCORING_WEIGHTS['exposure_score']*request.exposure_score + SCORING_WEIGHTS['urgency_score']*request.urgency_score + SCORING_WEIGHTS['confidence']*request.confidence)
    return round(score, 2)
def score_incident(request: IncidentScoreRequest) -> IncidentScoreResponse:
    priority_score = calculate_priority_score(request)
    severity = classify_severity(priority_score)
    matched_patterns = []
    if request.incident_type == "wildfire_haze":
        matched_patterns = match_wildfire_haze_patterns(
            request.hotspot_count,
            request.landuse_types,
            request.nearest_hotspot_distance_km,
        )
    return IncidentScoreResponse(area_id=request.area_id, incident_type=request.incident_type, priority_score=priority_score, severity=severity, recommended_action=recommended_action_for_severity(severity), operator_summary=build_operator_summary(severity, request.incident_type, request.risk_drivers), risk_drivers=request.risk_drivers, matched_patterns=matched_patterns)
