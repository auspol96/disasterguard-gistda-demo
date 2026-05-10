import json
from pathlib import Path
from app.actions import classify_severity, recommended_action_for_severity
from app.models import IncidentScoreRequest
from app.scoring import calculate_priority_score, score_incident

def test_priority_score_formula_for_wildfire_sample():
    req=IncidentScoreRequest(area_id='NTH-CHIANGMAI-001',incident_type='wildfire_haze',hazard_score=0.82,exposure_score=0.74,urgency_score=0.79,confidence=0.76,risk_drivers=[])
    assert calculate_priority_score(req)==0.78

def test_severity_thresholds():
    assert classify_severity(0.10)=='LOW'
    assert classify_severity(0.35)=='WATCH'
    assert classify_severity(0.55)=='MEDIUM'
    assert classify_severity(0.75)=='HIGH'
    assert classify_severity(0.90)=='CRITICAL'

def test_recommended_actions():
    assert recommended_action_for_severity('LOW')=='MONITOR_ONLY'
    assert recommended_action_for_severity('WATCH')=='KEEP_IN_MONITORING_QUEUE'
    assert recommended_action_for_severity('MEDIUM')=='REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE'
    assert recommended_action_for_severity('HIGH')=='PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE'
    assert recommended_action_for_severity('CRITICAL')=='IMMEDIATE_REVIEW_AND_ESCALATION'

def test_sample_outputs_match_scoring_engine():
    pairs=[('sample_inputs/wildfire_haze_chiangmai.json','sample_outputs/wildfire_priority_output.json'),('sample_inputs/rapid_flood_chiangrai.json','sample_outputs/flood_priority_output.json'),('sample_inputs/landslide_maehongson.json','sample_outputs/landslide_priority_output.json')]
    for ip,op in pairs:
        actual=score_incident(IncidentScoreRequest(**json.loads(Path(ip).read_text()))).model_dump()
        expected=json.loads(Path(op).read_text())
        assert actual==expected

def test_all_supported_incident_types_score_successfully():
    for t in ['wildfire_haze','rapid_flood','landslide']:
        req=IncidentScoreRequest(area_id='TEST-001',incident_type=t,hazard_score=.5,exposure_score=.5,urgency_score=.5,confidence=.5,risk_drivers=['demo signal'])
        res=score_incident(req)
        assert res.incident_type==t
        assert res.priority_score==0.5
        assert res.severity=='WATCH'
