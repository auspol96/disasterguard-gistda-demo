# DisasterGuard GISTDA Demo

DisasterGuard is a multi-sensor disaster-priority intelligence demo for Northern Thailand / ASEAN.

It is designed to complement existing disaster monitoring systems by helping rank which geolocated risk areas should receive earlier review, revisit, alerting, or response coordination.

This project is **not** intended to replace existing fire, drought, optical, SAR-enabled, weather, terrain, or community-risk systems. It is a decision-priority layer that can sit above multiple data sources.

## Initial MVP Scope

The first MVP supports three incident types:

1. `wildfire_haze`
2. `rapid_flood`
3. `landslide`

## API Endpoints

`GET /api/health`

`POST /api/incident/score`

## MVP Scoring Logic

```text
priority_score =
  0.40 × hazard_score
+ 0.30 × exposure_score
+ 0.20 × urgency_score
+ 0.10 × confidence
```

For the Chiang Mai wildfire/haze sample, this produces a priority score of `0.78`.

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Test with sample input

```bash
curl -X POST "http://127.0.0.1:8000/api/incident/score" \
  -H "Content-Type: application/json" \
  -d @sample_inputs/wildfire_haze_chiangmai.json
```

## Important Positioning

DisasterGuard does not claim deterministic disaster prediction.

The purpose is to support prioritization and decision-making by combining hazard, exposure, urgency, confidence, and explainable risk drivers into a compact operational output.

```text
DisasterGuard does not replace existing monitoring platforms.
It helps operators decide what deserves attention first.
```
