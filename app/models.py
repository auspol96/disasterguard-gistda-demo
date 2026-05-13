from typing import Any, Dict, List, Literal, Optional
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
    hotspot_count: Optional[int] = Field(default=None, ge=0)
    landuse_types: List[str] = Field(default_factory=list)
    nearest_hotspot_distance_km: Optional[float] = Field(default=None, ge=0.0)
    environmental_context: Dict[str, Any] = Field(default_factory=dict)

class IncidentPatternMatch(BaseModel):
    pattern_code: str
    pattern_name: str
    severity_hint: str
    explanation: str
    recommended_operational_focus: str

class IncidentScoreResponse(BaseModel):
    area_id: str
    incident_type: IncidentType
    priority_score: float
    severity: str
    recommended_action: str
    operator_summary: str
    risk_drivers: List[str]
    matched_patterns: List[IncidentPatternMatch] = Field(default_factory=list)
class HealthResponse(BaseModel):
    status: str
    service: str
