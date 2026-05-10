from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.config import SUPPORTED_INCIDENT_TYPES


class IncidentType(str, Enum):
    wildfire_haze = "wildfire_haze"
    rapid_flood = "rapid_flood"
    landslide = "landslide"


class Severity(str, Enum):
    LOW = "LOW"
    WATCH = "WATCH"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HealthResponse(BaseModel):
    status: str
    service: str


class IncidentScoreRequest(BaseModel):
    area_id: str = Field(..., min_length=1)
    incident_type: IncidentType = Field(
        ...,
        description=f"Supported values: {', '.join(SUPPORTED_INCIDENT_TYPES)}",
    )
    hazard_score: float = Field(..., ge=0.0, le=1.0)
    exposure_score: float = Field(..., ge=0.0, le=1.0)
    urgency_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_drivers: List[str] = Field(default_factory=list)


class IncidentScoreResponse(BaseModel):
    area_id: str
    incident_type: IncidentType
    priority_score: float
    severity: Severity
    recommended_action: str
    operator_summary: str
    risk_drivers: List[str]

