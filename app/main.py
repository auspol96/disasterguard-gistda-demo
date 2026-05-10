from fastapi import FastAPI

from app.config import SERVICE_NAME
from app.models import HealthResponse, IncidentScoreRequest, IncidentScoreResponse
from app.scoring import score_incident

app = FastAPI(
    title=SERVICE_NAME,
    description=(
        "A transparent disaster-priority intelligence demo for ranking areas "
        "that may deserve earlier review, revisit, alerting, or response coordination."
    ),
    version="0.1.0",
)


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME)


@app.post("/api/incident/score", response_model=IncidentScoreResponse)
def score_incident_endpoint(request: IncidentScoreRequest) -> IncidentScoreResponse:
    return score_incident(request)

