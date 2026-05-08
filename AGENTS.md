# Agent Instructions

This repository is a GISTDA-oriented DisasterGuard demo.

## Core Rules

1. Do not claim to replace GISTDA systems.
2. Position this project as a decision-priority layer.
3. Do not claim deterministic disaster prediction.
4. Focus on prioritization, review, revisit, alerting, and response coordination.
5. Keep the MVP simple, explainable, and demo-ready.
6. Initial incident types are:
   - `wildfire_haze`
   - `rapid_flood`
   - `landslide`
7. Keep scoring transparent and explainable.
8. Do not hardcode proprietary commercial formulas.
9. Include tests for all scoring logic.
10. Do not include private contact strategy, pricing, credentials, confidential proposal content, or institutional communications.

## Positioning Rules

DisasterGuard should be described as complementing existing and future disaster-monitoring capabilities, including:

- Fire Hotspot monitoring
- Crop Drought / เช็คแล้ง
- THEOS-2 optical imagery
- SAR-enabled disaster monitoring
- weather and rainfall data
- terrain and slope data
- community and infrastructure exposure data

Use language such as:

```text
DisasterGuard helps rank which geolocated areas deserve earlier review, revisit, alerting, or response coordination.
```

Avoid language such as:

```text
DisasterGuard predicts disasters with certainty.
DisasterGuard replaces existing GISTDA platforms.
DisasterGuard is a final operational emergency-response system.
```

## Engineering Rules

- Use Python and FastAPI for the MVP.
- Use Pydantic models for API input and output.
- Use pytest for tests.
- Keep dependencies lightweight.
- Keep all scoring logic explainable.
- Keep sample input/output files human-readable.
- Make sure the API can run locally using:

```bash
uvicorn app.main:app --reload
```

## Expected MVP Endpoints

```text
GET /api/health
POST /api/incident/score
```

## Expected Scoring Inputs

```text
area_id
incident_type
hazard_score
exposure_score
urgency_score
confidence
risk_drivers
```

## Expected Scoring Outputs

```text
area_id
incident_type
priority_score
severity
recommended_action
operator_summary
risk_drivers
```
