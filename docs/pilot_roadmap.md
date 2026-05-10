# Pilot Roadmap

## Phase 1: Local Demo Validation

- Validate the local FastAPI scoring API and dashboard flow.
- Review sample scenarios for wildfire / haze, rapid flood, and landslide.
- Confirm stakeholder messaging: decision-priority support, not deterministic prediction.

## Phase 2: Historical Incident Backtesting

- Select historical events and review outcomes.
- Convert historical signals into normalized input features.
- Compare priority scores against known review or response timelines.
- Identify calibration needs and missing risk drivers.

## Phase 3: Partner Data Integration

- Identify approved upstream data sources for hotspot, rainfall, terrain, vegetation stress, SAR surface water, and exposure layers.
- Define data refresh cadence and access method.
- Add controlled connectors or batch import workflows.

## Phase 4: Operational Dashboard Pilot

- Expand the dashboard from sample scenarios to pilot incident queues.
- Add operator review states and escalation notes.
- Test how priority results support coordination workflows.
- Keep existing monitoring systems as the source of hazard observations.

## Phase 5: Calibration And Production Hardening

- Refine scoring weights with domain experts and historical outcomes.
- Add audit trails, monitoring, authentication, and deployment controls.
- Improve reliability, validation, and governance before any operational use.
- Maintain clear positioning as a decision-priority layer that complements existing systems.

