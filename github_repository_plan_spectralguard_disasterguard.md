# GitHub Repository Plan for SpectralGuard and DisasterGuard

## Objective

This document defines what should be placed on GitHub for the current space-tech and disaster-intelligence projects.

The recommended approach is to create **two separate private repositories**:

1. `spectralguard-seldon`
2. `disasterguard-gistda-demo`

The reason for separation is simple:

- **SpectralGuard** is the Seldon-facing onboard hyperspectral validation package.
- **DisasterGuard** is the broader GISTDA-oriented multi-hazard decision-priority platform.

Do not mix both in one repository at this stage.

---

# 1. Repository A: `spectralguard-seldon`

## Purpose

This repository stores the submitted Seldon validation package.

It should remain focused on:

- onboard hyperspectral wildfire-readiness triage
- 22-band input compatibility
- lightweight trained anomaly model
- compact JSON alert output
- mission-priority action recommendation

This repository should **not** include the full commercial GISTDA strategy or proprietary future scoring logic.

## Recommended folder structure

```text
spectralguard-seldon/
│
├── README.md
├── AGENTS.md
├── requirements.txt
├── main.py
├── config.yaml
│
├── spectralguard/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── band_adapter.py
│   ├── spectral_indices.py
│   ├── feature_engineering.py
│   ├── anomaly_model.py
│   ├── risk_fusion.py
│   ├── action_policy.py
│   └── output_schema.py
│
├── scripts/
│   ├── train_demo_model.py
│   ├── benchmark_inference.py
│   └── package_submission.py
│
├── models/
│   ├── README.md
│   ├── anomaly_model.pkl
│   ├── scaler.pkl
│   ├── feature_columns.json
│   └── anomaly_calibration.json
│
├── sample_data/
│   ├── sample_tile_22bands.csv
│   ├── sample_tile_22bands_normal.csv
│   └── band_metadata.json
│
├── output_example/
│   ├── high_risk_alert.json
│   └── normal_alert.json
│
├── docs/
│   ├── seldon_submission_summary.md
│   ├── algorithm_description.md
│   ├── onboard_execution_plan.md
│   ├── validation_report.md
│   ├── model_card.md
│   ├── ip_note.md
│   └── real_data_upgrade_plan.md
│
└── tests/
    └── test_pipeline.py
```

## `AGENTS.md` for `spectralguard-seldon`

Create a file named `AGENTS.md` with this content:

```text
# Agent Instructions

This repository is a validation package for SpectralGuard Lite.

Rules:
1. Do not claim deterministic wildfire prediction.
2. Use "wildfire-readiness", "vegetation-stress triage", or "mission-priority alert".
3. Maintain 22-band input compatibility.
4. Keep the package IP-safe.
5. Do not add proprietary contextual acceleration logic.
6. Do not add GISTDA commercial strategy.
7. Keep all code CPU-only and lightweight.
8. Every change must include or update tests.
9. Keep version labels consistent.
10. Output must remain compact JSON alerts.
```

## First Git commit

Inside the `spectralguard_seldon_package` folder:

```bash
git init
git add .
git commit -m "Initial SpectralGuard Lite v0.2.1 Seldon validation package"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Suggested first Codex tasks

### Task 1: Version consistency and smoke tests

```text
Review this repository as a Seldon onboard algorithm validation package.

Fix version consistency to v0.2.1 across all files.

Ensure main.py runs both sample inputs successfully.

Add a smoke test that validates:
1. high-risk sample outputs MEDIUM or higher
2. normal sample outputs NORMAL
3. output JSON includes risk_score, severity, confidence, novelty_score, recommended_action, risk_factors, and risk_drivers.

Do not change the public concept or add proprietary commercial logic.

Create a PR with the changes.
```

### Task 2: Inference benchmark

```text
Add a benchmark script scripts/benchmark_inference.py that measures average inference time over 100 runs for both sample_tile_22bands.csv and sample_tile_22bands_normal.csv.

Write the results to docs/inference_benchmark.md.

Keep the script lightweight and compatible with CPU-only execution.

Create a PR.
```

### Task 3: Package script

```text
Add scripts/package_submission.py that creates spectralguard_seldon_package_v0_2_1_final.zip while excluding venv, __pycache__, .DS_Store, .git, and test output files.

The script should print the package size and list included top-level folders.

Create a PR.
```

### Task 4: Real-data upgrade plan

```text
Add docs/real_data_upgrade_plan.md describing the v0.3 path:
PRISMA / EnMAP data acquisition, 22-band resampling, real-data anomaly model training, validation against hotspot/burn-area references, and limitations.

Keep it technical but do not overclaim operational wildfire prediction.

Create a PR.
```

---

# 2. Repository B: `disasterguard-gistda-demo`

## Purpose

This repository should contain the broader GISTDA-oriented demo.

It should position the product as a **multi-sensor disaster-priority intelligence layer**, not as a replacement for GISTDA systems.

The system should complement:

- GISTDA Fire Hotspot platform
- Crop Drought / เช็คแล้ง
- THEOS-2 optical imagery
- SAR / ICEYE capability
- weather data
- terrain and slope data
- community and infrastructure exposure data

## Recommended folder structure

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

## Initial MVP scope

Start with only three incident types:

```text
1. wildfire_haze
2. rapid_flood
3. landslide
```

Do not build Crop Drought as a competing module.

Crop Drought should be treated as an **upstream input signal** from GISTDA, not as the main product.

## MVP API endpoints

```text
POST /api/incident/score
GET /api/health
```

## Example input

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

## Example output

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

## `AGENTS.md` for `disasterguard-gistda-demo`

Create a file named `AGENTS.md` with this content:

```text
# Agent Instructions

This repository is a GISTDA-oriented DisasterGuard demo.

Rules:
1. Do not claim to replace GISTDA systems.
2. Position this as a decision-priority layer.
3. Mention that it complements Fire Hotspot, Crop Drought, THEOS-2, SAR/ICEYE, weather, terrain, and community exposure data.
4. Do not claim deterministic disaster prediction.
5. Focus on prioritization, review, revisit, and response coordination.
6. Initial incident types are wildfire_haze, rapid_flood, and landslide.
7. Keep scoring explainable.
8. Do not hardcode proprietary commercial formulas.
9. Include tests for all scoring logic.
10. Keep the MVP simple and demo-ready.
```

## Suggested first Codex task for DisasterGuard

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
- recommended_action logic
- sample JSON inputs
- pytest tests
- README.md
- docs/gistda_demo_positioning.md

Do not claim deterministic disaster prediction.
Position the system as a decision-priority layer that complements GISTDA’s existing Fire Hotspot, Crop Drought, THEOS-2, and future SAR/ICEYE capability.
```

---

# Recommended `.gitignore`

Use this in both repositories:

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

# What should remain private

Do not put these into GitHub yet:

```text
GISTDA private contact strategy
commercial pricing
full contextual acceleration formula
human activity ignition model
detailed government proposal
API keys
real credentials
private Seldon communication
full EdgeMind roadmap
```

---

# Recommended sequence

## Step 1: Create `spectralguard-seldon`

Use the submitted Seldon package as the base.

Push it to a private GitHub repo.

Then use Codex for:

```text
1. version consistency
2. smoke tests
3. inference benchmark
4. packaging script
5. real-data upgrade plan
```

## Step 2: Create `disasterguard-gistda-demo`

Use Codex to build the FastAPI MVP.

Focus on:

```text
wildfire_haze
rapid_flood
landslide
priority score
recommended action
operator summary
```

## Step 3: Keep repositories private

Do not make either repository public until the IP strategy is clearer.

---

# Strategic Summary

## SpectralGuard

```text
Seldon-facing module
Onboard hyperspectral wildfire-readiness triage
22-band compatible
Satellite algorithm validation package
```

## DisasterGuard

```text
GISTDA-facing platform
Multi-sensor disaster-priority intelligence layer
Combines existing GISTDA systems and future SAR/ICEYE capability
Ranks where to review, revisit, alert, or coordinate response first
```

The best approach is:

```text
SpectralGuard proves technical space capability.
DisasterGuard becomes the broader institutional product for GISTDA.
```
