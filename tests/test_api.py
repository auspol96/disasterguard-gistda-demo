from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health_endpoint():
    r=client.get('/api/health')
    assert r.status_code==200
    assert r.json()=={'status':'ok','service':'DisasterGuard GISTDA Demo'}

def test_incident_score_endpoint_wildfire():
    payload={'area_id':'NTH-CHIANGMAI-001','incident_type':'wildfire_haze','hazard_score':0.82,'exposure_score':0.74,'urgency_score':0.79,'confidence':0.76,'risk_drivers':['recent hotspot cluster','vegetation stress','low humidity','wind spread potential','nearby community exposure']}
    r=client.post('/api/incident/score',json=payload)
    assert r.status_code==200
    d=r.json()
    assert d['priority_score']==0.78
    assert d['severity']=='HIGH'
    assert d['recommended_action']=='PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE'

def test_invalid_score_rejected():
    payload={'area_id':'NTH-CHIANGMAI-001','incident_type':'wildfire_haze','hazard_score':1.2,'exposure_score':0.74,'urgency_score':0.79,'confidence':0.76,'risk_drivers':[]}
    assert client.post('/api/incident/score',json=payload).status_code==422

def test_invalid_incident_type_rejected():
    payload={'area_id':'NTH-CHIANGMAI-001','incident_type':'earthquake','hazard_score':0.82,'exposure_score':0.74,'urgency_score':0.79,'confidence':0.76,'risk_drivers':[]}
    assert client.post('/api/incident/score',json=payload).status_code==422
