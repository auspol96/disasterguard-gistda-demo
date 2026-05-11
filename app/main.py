from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import SERVICE_NAME
from app.models import HealthResponse, IncidentScoreRequest, IncidentScoreResponse
from app.scoring import score_incident

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
LIVE_CONTEXT_DIR = ROOT_DIR / "live_context"

app = FastAPI(
    title="DisasterGuard GISTDA Demo",
    description=(
        "A multi-sensor disaster-priority intelligence demo for prioritization, "
        "review, revisit, alerting, and response coordination."
    ),
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount(
    "/live_context",
    StaticFiles(directory=LIVE_CONTEXT_DIR, check_dir=False),
    name="live_context",
)


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME)


@app.post("/api/incident/score", response_model=IncidentScoreResponse)
def incident_score(request: IncidentScoreRequest) -> IncidentScoreResponse:
    return score_incident(request)
