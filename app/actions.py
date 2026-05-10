def classify_severity(priority_score: float) -> str:
    if priority_score >= 0.90: return "CRITICAL"
    if priority_score >= 0.75: return "HIGH"
    if priority_score >= 0.55: return "MEDIUM"
    if priority_score >= 0.35: return "WATCH"
    return "LOW"
def recommended_action_for_severity(severity: str) -> str:
    return {"LOW":"MONITOR_ONLY","WATCH":"KEEP_IN_MONITORING_QUEUE","MEDIUM":"REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE","HIGH":"PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE","CRITICAL":"IMMEDIATE_REVIEW_AND_ESCALATION"}[severity]
def build_operator_summary(severity: str, incident_type: str, risk_drivers: list[str]) -> str:
    label = incident_type.replace('_', ' ')
    if not risk_drivers: drivers = 'the submitted hazard, exposure, urgency, and confidence signals'
    elif len(risk_drivers) == 1: drivers = risk_drivers[0]
    else: drivers = ', '.join(risk_drivers[:-1]) + f", and {risk_drivers[-1]}"
    if severity in {'HIGH','CRITICAL'}:
        return f"This {label} area should be prioritized due to elevated hazard, exposure, and urgency signals, including {drivers}."
    if severity == 'MEDIUM':
        return f"This {label} area should be reviewed in the next operational cycle due to moderate priority signals, including {drivers}."
    if severity == 'WATCH':
        return f"This {label} area should remain in the monitoring queue. Current drivers include {drivers}."
    return f"This {label} area currently requires monitoring only. No immediate escalation is recommended."
