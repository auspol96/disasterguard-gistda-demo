# GitHub Repository Plan for DisasterGuard GISTDA Demo

## Objective

This document defines what should be placed on GitHub for the **GISTDA-oriented DisasterGuard project**.

The project should be positioned as a:

```text
Multi-sensor disaster-priority intelligence layer
```

It should **not** be positioned as a replacement for existing GISTDA systems.

The system should complement GISTDA’s existing and emerging capabilities, including:

- Fire Hotspot monitoring
- Crop Drought / เช็คแล้ง
- THEOS-2 optical imagery
- SAR-enabled disaster monitoring, including future partnership-based capability
- weather and rainfall data
- terrain and slope data
- community and infrastructure exposure data

---

# Repository Name

Recommended private GitHub repository name:

```text
disasterguard-gistda-demo
```

Keep this repository **private** at this stage.

---

# Product Positioning

## Core positioning

```text
DisasterGuard is a multi-sensor disaster-priority intelligence layer that helps rank which geolocated areas should receive earlier review, revisit, alerting, or response coordination across wildfire/haze, rapid flooding, and landslide scenarios.
```

## What DisasterGuard is

DisasterGuard is:

```text
A decision-priority layer
A multi-hazard scoring engine
A demo API for incident prioritization
A future dashboard-ready intelligence layer
A system that supports operator review and response coordination
```

## What DisasterGuard is not

DisasterGuard is not:

```text
A replacement for GISTDA Fire Hotspot
A replacement for Crop Drought
A replacement for THEOS-2 imagery
A replacement for SAR providers
A deterministic disaster prediction system
A public disaster map clone
```

---

# Recommended Folder Structure

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
│   └── config.py
│
├── sample_inputs/
│   ├── wildfire_haze_chiangmai.json
│   ├── rapid_flood_chiangrai.json
│   └── landslide_maehongson.json
│
├── sample_outputs/
│   ├── wildfire_priority_output.json
│   ├── flood_priority_output.json
│   └── landslide_priority_output.json
│
├── docs/
│   ├── gistda_demo_positioning.md
│   ├── system_architecture.md
│   ├── data_source_mapping.md
│   ├── scoring_logic.md
│   ├── demo_story.md
│   └── roadmap.md
│
└── tests/
    ├── test_scoring.py
    └── test_api.py
```

---

# Initial MVP Scope

Start with only three incident types:

```text
1. wildfire_haze
2. rapid_flood
3. landslide
```

Do not build Crop Drought as a competing product.

Crop Drought should be treated as an **upstream input signal**, not the main product.

---

# Conceptual System Architecture

```text
Existing monitoring systems and data sources
        ↓
Multi-source data connector
        ↓
Hazard-specific scoring
        ↓
Community / asset exposure scoring
        ↓
Urgency and confidence scoring
        ↓
Priority fusion engine
        ↓
Recommended action
        ↓
API / dashboard / alert output
```

---

# Data Source Mapping

## 1. Wildfire / Haze Priority

Possible input signals:

```text
Fire hotspot points
Hotspot age
Hotspot cluster density
Vegetation stress signal
Drought or dryness signal
Humidity
Temperature
Wind speed / wind direction
Forest boundary
Agricultural burning zones
Historical hotspot recurrence
Nearby settlement / school / hospital / road exposure
```

Output:

```text
Wildfire/haze priority score
Severity
Risk drivers
Recommended review or response action
```

---

## 2. Rapid Flood / Flash Flood Priority

Possible input signals:

```text
Rainfall accumulation
Rainfall intensity
River proximity
Floodplain / low-lying terrain
Slope and drainage pattern
SAR-observed surface water expansion
Soil saturation proxy
Land cover
Nearby community / road / bridge / critical infrastructure exposure
```

Output:

```text
Flood priority score
Severity
Risk drivers
Recommended review or response action
```

---

## 3. Landslide / Slope Failure Priority

Possible input signals:

```text
Heavy rainfall accumulation
Slope angle
Elevation / DEM
Soil moisture proxy
Land-cover change
Deforestation / vegetation loss
Road cutting / construction proximity
Historical landslide recurrence
Nearby community or transport route exposure
```

Output:

```text
Landslide priority score
Severity
Risk drivers
Recommended review or response action
```

---

# MVP API Endpoints

## Health check

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

## Incident scoring

```text
POST /api/incident/score
```

---

# Example Input

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

---

# Example Output

```json
{
  "area_id": "NTH-CHIANGMAI-001",
  "incident_type": "wildfire_haze",
  "priority_score": 0.80,
  "severity": "HIGH",
  "recommended_action": "PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE",
  "operator_summary": "This area should be prioritized due to elevated hazard, exposure, and urgency signals."
}
```

---

# Priority Scoring Logic

For the first MVP, keep the formula simple and explainable.

Recommended demo formula:

```text
priority_score =
  0.40 × hazard_score
+ 0.30 × exposure_score
+ 0.20 × urgency_score
+ 0.10 × confidence
```

This is not a final production formula.

It is only a transparent MVP scoring method to demonstrate the concept.

---

# Severity Logic

Recommended severity thresholds:

```text
0.00–0.34 = LOW
0.35–0.54 = WATCH
0.55–0.74 = MEDIUM
0.75–0.89 = HIGH
0.90–1.00 = CRITICAL
```

---

# Recommended Actions

## LOW

```text
MONITOR_ONLY
```

## WATCH

```text
KEEP_IN_MONITORING_QUEUE
```

## MEDIUM

```text
REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE
```

## HIGH

```text
PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE
```

## CRITICAL

```text
IMMEDIATE_REVIEW_AND_ESCALATION
```

---

# `AGENTS.md`

Create a file named `AGENTS.md` with this content:

```text
# Agent Instructions

This repository is a GISTDA-oriented DisasterGuard demo.

Rules:
1. Do not claim to replace GISTDA systems.
2. Position this as a decision-priority layer.
3. Mention that it complements Fire Hotspot, Crop Drought, THEOS-2, SAR-enabled disaster monitoring, weather, terrain, and community exposure data.
4. Do not claim deterministic disaster prediction.
5. Focus on prioritization, review, revisit, alerting, and response coordination.
6. Initial incident types are wildfire_haze, rapid_flood, and landslide.
7. Keep scoring explainable.
8. Do not hardcode proprietary commercial formulas.
9. Include tests for all scoring logic.
10. Keep the MVP simple and demo-ready.
11. Do not include private contact strategy, pricing, credentials, or confidential proposal content.
```

---

# Recommended `.gitignore`

Use this file:

```text
venv/
__pycache__/
.DS_Store
.env
*.log
*.zip
*.sqlite3
outputs/tmp/
.pytest_cache/
```

---

# Suggested README Opening

```text
# DisasterGuard GISTDA Demo

DisasterGuard is a multi-sensor disaster-priority intelligence demo for Northern Thailand / ASEAN.

It is designed to complement existing disaster monitoring systems by ranking which geolocated risk areas should receive earlier review, revisit, alerting, or response coordination.

The first MVP supports three incident types:

1. wildfire_haze
2. rapid_flood
3. landslide

This demo does not claim deterministic disaster prediction. It is a decision-priority layer that combines hazard, exposure, urgency, confidence, and explainable risk drivers into a compact priority output.
```

---

# Suggested Codex Task

Use this as the first Codex prompt:

```text
Create a FastAPI MVP for DisasterGuard, a multi-sensor disaster-priority intelligence layer for Northern Thailand / ASEAN.

The API should support incident scoring for:
1. wildfire_haze
2. rapid_flood
3. landslide

Create:
- POST /api/incident/score
- GET /api/health
- Pydantic input/output models
- scoring engine using hazard_score, exposure_score, urgency_score, confidence
- severity classification
- recommended_action logic
- operator_summary generation
- sample JSON inputs
- sample JSON outputs
- pytest tests
- README.md
- AGENTS.md
- docs/gistda_demo_positioning.md
- docs/system_architecture.md
- docs/data_source_mapping.md
- docs/scoring_logic.md
- docs/demo_story.md
- docs/roadmap.md

Do not claim deterministic disaster prediction.
Do not claim to replace existing GISTDA systems.
Position the system as a decision-priority layer that complements existing fire, drought, optical, SAR-enabled, weather, terrain, and community exposure data sources.
Keep the scoring transparent and explainable.
```

---

# What Should Remain Private

Do not put these into GitHub yet:

```text
private contact strategy
commercial pricing
full proprietary scoring formula
human activity ignition model
detailed government proposal
API keys
real credentials
private institutional communications
full commercial roadmap
```

---

# Recommended Build Sequence

## Step 1: Create private GitHub repository

```text
disasterguard-gistda-demo
```

## Step 2: Add base files

```text
README.md
AGENTS.md
requirements.txt
.gitignore
```

## Step 3: Use Codex to generate FastAPI MVP

Use the Codex prompt above.

## Step 4: Test locally

Expected commands:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

## Step 5: Prepare demo story

Focus on:

```text
Northern Thailand wildfire/haze priority
Chiang Rai rapid flood priority
Mae Hong Son landslide priority
```

---

# Strategic Summary

DisasterGuard should be the GISTDA-facing platform.

Its role is:

```text
Combine hazard signals, exposure, urgency, and confidence
→ rank the highest-priority areas
→ explain why the area matters
→ recommend review, revisit, alerting, or response coordination
```

The winning message is:

```text
DisasterGuard does not replace existing monitoring platforms.
It helps operators decide what deserves attention first.
```
