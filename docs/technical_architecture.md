# Technical Architecture

## Current Data Flow

```text
sample_data CSVs
        |
        v
scripts/build_incident_inputs.py
        |
        v
generated JSON files in sample_inputs/
        |
        v
FastAPI scoring API
        |
        v
browser dashboard
```

## Components

### Sample Data CSVs

The `sample_data/` folder contains small open-data-style CSV files for wildfire hotspots, rainfall, terrain / exposure, and vegetation stress. These are demonstration inputs only.

### Data Preparation Script

`scripts/build_incident_inputs.py` reads the sample CSVs and converts them into JSON payloads matching the existing `IncidentScoreRequest` schema.

### Generated JSON Inputs

Generated files are written to `sample_inputs/` and can be submitted to the existing scoring API.

### FastAPI Scoring API

The API receives incident scoring payloads, applies the transparent weighted scoring formula, classifies severity, and returns a recommended action and operator summary.

### Browser Dashboard

The dashboard calls the scoring API, ranks sample incidents, shows a mock priority map, displays selected incident details, and lists relevant data-source readiness layers.

## Current Limitations

- Uses sample data only.
- No live GISTDA integration.
- No production GIS layer.
- No operational alerting.
- No database or persistence layer.
- Scoring weights are transparent demo weights, not calibrated production logic.

## Future Integration Possibilities

- Connect approved fire hotspot, rainfall, terrain, SAR, and exposure data sources.
- Add historical incident backtesting for score calibration.
- Integrate with GISTDA or partner geospatial services where appropriate.
- Add operator feedback capture and audit trails.
- Add role-based dashboard views for review, escalation, and coordination workflows.

