from typing import List, Literal
from pydantic import BaseModel, Field
IncidentType = Literal["wildfire_haze", "rapid_flood", "landslide"]
class IncidentScoreRequest(BaseModel):
    area_id: str = Field(..., min_length=1)
    incident_type: IncidentType
    hazard_score: float = Field(..., ge=0.0, le=1.0)
    exposure_score: float = Field(..., ge=0.0, le=1.0)
    urgency_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_drivers: List[str] = Field(default_factory=list)
class IncidentScoreResponse(BaseModel):
    area_id: str
    incident_type: IncidentType
    priority_score: float
    severity: str
    recommended_action: str
    operator_summary: str
    risk_drivers: List[str]
class HealthResponse(BaseModel):
    status: str
    service: str
