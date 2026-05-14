from dotenv import load_dotenv
load_dotenv()

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.briefing import build_daily_briefing
from app.config import SERVICE_NAME
from app.forest_priority import (
    apply_change_status_to_areas,
    build_action_queue,
    build_change_summary,
    build_explainable_ranking_th,
    build_province_summary,
    determine_response_priority,
    load_monitored_areas,
    previous_ranking_path_for,
    read_ranking_payload,
    refresh_forest_priority_ranking,
)
from app.models import HealthResponse, IncidentScoreRequest, IncidentScoreResponse
from app.recurrence_context import (
    is_confirmed_gistda_recurrence,
    normalize_gistda_recurrence_response,
)
from app.scoring import score_incident
from scripts.fetch_gistda_hotspot_context import refresh_hotspot_context

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
LIVE_CONTEXT_DIR = ROOT_DIR / "live_context"
MONITORED_FOREST_AREAS_PATH = ROOT_DIR / "config" / "monitored_forest_areas.json"
FOREST_PRIORITY_RANKING_PATH = LIVE_CONTEXT_DIR / "forest_priority_ranking.json"

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

@app.get("/api/gistda/hotspot-context")
def gistda_hotspot_context():
    context_path = BASE_DIR.parent / "live_context" / "gistda_hotspot_context.json"

    if not context_path.exists():
        return {
            "status": "not_loaded",
            "message": "GISTDA hotspot context not loaded yet. Run scripts/fetch_gistda_hotspot_context.py first.",
            "summary": {
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
            },
        }

    try:
        with context_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "summary": {
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
            },
        }


@app.post("/api/gistda/refresh-hotspot-context")
def gistda_refresh_hotspot_context() -> JSONResponse:
    if not os.getenv("GISTDA_API_KEY"):
        payload = {
            "status": "not_configured",
            "message": "GISTDA_API_KEY environment variable is not configured.",
            "context_path": None,
            "generated_input_path": None,
            "summary": {
                "status": "not_configured",
                "source_satellites_checked": [],
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
                "raw_limited_sample": [],
            },
        }
        return JSONResponse(status_code=503, content=payload)

    try:
        result = refresh_hotspot_context()
    except Exception:
        payload = {
            "status": "error",
            "message": "Unable to refresh GISTDA hotspot context.",
            "context_path": None,
            "generated_input_path": None,
            "summary": {
                "status": "error",
                "source_satellites_checked": [],
                "hotspot_count": 0,
                "dates_available": [],
                "nearest_hotspot_distance_km": None,
                "provinces_detected": [],
                "landuse_types": [],
                "raw_limited_sample": [],
            },
        }
        return JSONResponse(status_code=500, content=payload)

    status_code = 200 if result["status"] == "ok" else 502
    return JSONResponse(status_code=status_code, content=result)


@app.get("/api/forest-priority/areas")
def forest_priority_areas() -> JSONResponse:
    try:
        return JSONResponse(content=load_monitored_areas(MONITORED_FOREST_AREAS_PATH))
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Unable to load monitored forest area configuration.",
                "areas": [],
            },
        )


def load_current_forest_priority_ranking() -> dict | None:
    if not FOREST_PRIORITY_RANKING_PATH.exists():
        return None

    with FOREST_PRIORITY_RANKING_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    previous_payload = read_ranking_payload(previous_ranking_path_for(FOREST_PRIORITY_RANKING_PATH))
    for area in payload.get("areas", []):
        area.setdefault("matched_patterns", [])
        area.setdefault("environmental_context", {})
        area["recurrence_context"] = normalize_gistda_recurrence_response(
            area.get("recurrence_context", {})
        )
        if not is_confirmed_gistda_recurrence(area["recurrence_context"]):
            area["risk_drivers"] = [
                driver
                for driver in area.get("risk_drivers", [])
                if driver != "พื้นที่มีประวัติความเสี่ยงซ้ำซากจาก GISTDA"
            ]
            area["matched_patterns"] = [
                pattern
                for pattern in area.get("matched_patterns", [])
                if pattern.get("pattern_code") != "RECURRENT_RISK_AREA"
            ]
        area["response_priority"] = determine_response_priority(area)
        area["explainable_ranking_th"] = build_explainable_ranking_th(area)
    apply_change_status_to_areas(payload, previous_payload)
    payload["province_summary"] = build_province_summary(payload.get("areas", []))
    payload["action_queue"] = build_action_queue(payload.get("areas", []))
    payload["change_summary"] = build_change_summary(payload, previous_payload)
    return payload


@app.get("/api/forest-priority/ranking")
def forest_priority_ranking() -> JSONResponse:
    if not FOREST_PRIORITY_RANKING_PATH.exists():
        return JSONResponse(
            status_code=404,
            content={
                "status": "not_loaded",
                "message": "Forest priority ranking not generated yet. Call POST /api/forest-priority/refresh-ranking first.",
                "areas": [],
            },
        )

    try:
        payload = load_current_forest_priority_ranking()
        return JSONResponse(content=payload)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Unable to load forest priority ranking.",
                "areas": [],
            },
        )


@app.get("/api/briefing/daily")
def daily_briefing() -> JSONResponse:
    if not FOREST_PRIORITY_RANKING_PATH.exists():
        return JSONResponse(
            status_code=404,
            content={
                "status": "not_loaded",
                "message": "Forest priority ranking not generated yet. Call POST /api/forest-priority/refresh-ranking first.",
            },
        )

    try:
        ranking = load_current_forest_priority_ranking()
        return JSONResponse(content=build_daily_briefing(ranking))
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Unable to generate daily briefing.",
            },
        )


@app.post("/api/forest-priority/refresh-ranking")
def forest_priority_refresh_ranking() -> JSONResponse:
    if not os.getenv("GISTDA_API_KEY"):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_configured",
                "message": "GISTDA_API_KEY environment variable is not configured.",
                "areas": [],
            },
        )

    try:
        payload = refresh_forest_priority_ranking(
            MONITORED_FOREST_AREAS_PATH,
            FOREST_PRIORITY_RANKING_PATH,
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Unable to refresh forest priority ranking.",
                "areas": [],
            },
        )

    return JSONResponse(status_code=200, content=payload)
