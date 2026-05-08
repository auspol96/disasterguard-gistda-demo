# DisasterGuard GISTDA Demo Project Plan

## Objective

DisasterGuard is a multi-sensor disaster-priority intelligence demo for Northern Thailand / ASEAN.

The purpose is to help rank which geolocated risk areas should receive earlier review, revisit, alerting, or response coordination.

This project should be treated as a **decision-priority layer**, not a replacement for existing disaster-monitoring systems.

---

# Product Positioning

## Core Positioning

```text
DisasterGuard is a multi-sensor disaster-priority intelligence layer that combines hazard, exposure, urgency, confidence, and explainable risk drivers to help operators prioritize disaster-risk areas.
```

## What DisasterGuard Is

DisasterGuard is:

```text
A decision-priority layer
A multi-hazard scoring engine
A demo API for incident prioritization
A future dashboard-ready intelligence layer
A system that supports operator review and response coordination
```

## What DisasterGuard Is Not

DisasterGuard is not:

```text
A replacement for Fire Hotspot monitoring
A replacement for Crop Drought / เช็คแล้ง
A replacement for THEOS-2 imagery
A replacement for SAR providers
A deterministic disaster prediction system
A public disaster map clone
```

---

# Initial MVP Scope

The first MVP supports three incident types:

```text
1. wildfire_haze
2. rapid_flood
3. landslide
```

Do not build Crop Drought as a competing product.

Crop Drought should be treated as an **upstream input signal**, not the main product.

---

# Conceptual Architecture

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

Expected output:

```text
wildfire/haze priority score
severity
risk drivers
recommended review or response action
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

Expected output:

```text
flood priority score
severity
risk drivers
recommended review or response action
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

Expected output:

```text
landslide priority score
severity
risk drivers
recommended review or response action
```

---

# MVP API Endpoints

## Health Check

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

## Incident Scoring

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
  "priority_score": 0.80,
  "severity": "HIGH",
  "recommended_action": "PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE",
  "operator_summary": "This area should be prioritized due to elevated hazard, exposure, and urgency signals.",
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

This is a transparent MVP formula, not a final production model.

---

# Severity Logic

```text
0.00–0.34 = LOW
0.35–0.54 = WATCH
0.55–0.74 = MEDIUM
0.75–0.89 = HIGH
0.90–1.00 = CRITICAL
```

---

# Recommended Actions

| Severity | Recommended Action |
|---|---|
| LOW | `MONITOR_ONLY` |
| WATCH | `KEEP_IN_MONITORING_QUEUE` |
| MEDIUM | `REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE` |
| HIGH | `PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE` |
| CRITICAL | `IMMEDIATE_REVIEW_AND_ESCALATION` |

---

# Recommended Repository Structure

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
│   ├── project_plan.md
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

# Suggested Codex Prompt

```text
Read README.md, AGENTS.md, and docs/project_plan.md.

Create the FastAPI MVP described in the project plan for DisasterGuard, a multi-sensor disaster-priority intelligence layer for Northern Thailand / ASEAN.

Implement:
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
- documentation files listed in the project plan

Follow these constraints:
- Do not claim deterministic disaster prediction.
- Do not claim to replace existing GISTDA systems.
- Keep scoring transparent and explainable.
- Keep the MVP simple and demo-ready.

Create a PR with the changes.
```
