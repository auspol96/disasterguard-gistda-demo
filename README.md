# DisasterGuard GISTDA Demo

DisasterGuard is a multi-sensor disaster-priority intelligence demo for Northern Thailand / ASEAN.

It is designed to complement existing disaster monitoring systems by helping rank which geolocated risk areas should receive earlier review, revisit, alerting, or response coordination.

This project is **not** intended to replace existing fire, drought, optical, SAR-enabled, weather, terrain, or community-risk systems. It is a decision-priority layer that can sit above multiple data sources.

## Initial MVP Scope

The first MVP supports three incident types:

1. `wildfire_haze`
2. `rapid_flood`
3. `landslide`

## Core Concept

DisasterGuard combines:

```text
hazard_score
+ exposure_score
+ urgency_score
+ confidence
+ risk_drivers
→ priority_score
→ severity
→ recommended_action
→ operator_summary
```

## Example Use Case

For a wildfire/haze scenario in Northern Thailand, the system may receive signals such as:

```text
recent hotspot cluster
vegetation stress
low humidity
wind spread potential
nearby community exposure
```

It then returns a priority score and recommended action for operator review.

## API Endpoints

### Browser Dashboard

```text
GET /
```

The root path serves a simple dark-mode operations dashboard. It lets an operator select one of three sample scenarios and sends the selected payload to `POST /api/incident/score`.

The dashboard displays:

```text
area_id
incident_type
priority_score
severity
recommended_action
risk_drivers
operator_summary
```

It is intentionally simple: no React, no database, and no real map library or live map layer yet. The dashboard includes an HTML/CSS mock priority panel for demo context while keeping DisasterGuard positioned as a decision-priority layer for operator review and coordination.

### Health Check

```text
GET /api/health
```

Expected output:

```json
{
  "status": "ok",
  "service": "DisasterGuard GISTDA Demo"
}
```

### Incident Scoring

```text
POST /api/incident/score
```

Example input:

```json
{
  "area_id": "NTH-CHIANGMAI-001",
  "incident_type": "wildfire_haze",
  "hazard_score": 0.82,
  "exposure_score": 0.74,
  "urgency_score": 0.79,
  "confidence": 0.76,
  "risk_drivers": [
    "recent hotspot cluster",
    "vegetation stress",
    "low humidity",
    "wind spread potential",
    "nearby community exposure"
  ]
}
```

Example output:

```json
{
  "area_id": "NTH-CHIANGMAI-001",
  "incident_type": "wildfire_haze",
  "priority_score": 0.8,
  "severity": "HIGH",
  "recommended_action": "PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE",
  "operator_summary": "This area should be prioritized due to elevated hazard, exposure, and urgency signals."
}
```

## MVP Scoring Logic

The first demo uses an explainable scoring formula:

```text
priority_score =
  0.40 × hazard_score
+ 0.30 × exposure_score
+ 0.20 × urgency_score
+ 0.10 × confidence
```

This is a transparent MVP formula, not a final production model.

## Severity Logic

```text
0.00–0.34 = LOW
0.35–0.54 = WATCH
0.55–0.74 = MEDIUM
0.75–0.89 = HIGH
0.90–1.00 = CRITICAL
```

## Recommended Actions

| Severity | Recommended Action |
|---|---|
| LOW | `MONITOR_ONLY` |
| WATCH | `KEEP_IN_MONITORING_QUEUE` |
| MEDIUM | `REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE` |
| HIGH | `PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE` |
| CRITICAL | `IMMEDIATE_REVIEW_AND_ESCALATION` |

## Local Development

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Repository Structure

```text
disasterguard-gistda-demo/
│
├── README.md
├── AGENTS.md
├── requirements.txt
├── .gitignore
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── scoring.py
│   ├── actions.py
│   ├── config.py
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── sample_inputs/
├── sample_outputs/
├── docs/
└── tests/
```

## Important Positioning

DisasterGuard does not claim deterministic disaster prediction.

The purpose is to support prioritization and decision-making by combining hazard, exposure, urgency, confidence, and explainable risk drivers into a compact operational output.

The winning message:

```text
DisasterGuard does not replace existing monitoring platforms.
It helps operators decide what deserves attention first.
```
