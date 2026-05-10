# DisasterGuard Demo Script

## 1. Opening

Introduce DisasterGuard as a multi-hazard decision-priority layer. Use language such as:

```text
DisasterGuard helps operators rank which geolocated risk areas deserve earlier review, revisit, alerting, or response coordination.
```

Clarify that the local dashboard is a pilot demo using sample inputs and transparent scoring.

## 2. Executive Overview

Show the Executive Overview section first. Explain that it summarizes the number of monitored sample incidents, counts by severity, and the current top concern based on the highest priority score.

Suggested phrasing:

```text
This panel gives supervisors a fast view of current review pressure across the monitored sample incidents.
```

## 3. Priority Queue

Move to the Priority Queue. Explain that the dashboard calls the existing scoring API for each sample incident and ranks the results by priority score.

Click a row and show that the selected incident updates the map marker, detail panel, and data-source readiness panel.

## 4. Mock Map Priority View

Show the mock map panel. Explain that it is intentionally lightweight and uses no real GIS library in this milestone. The markers are used to demonstrate how a priority layer might sit above existing monitoring and geospatial tools.

## 5. Incident Detail Panel

Review the selected incident details:

- Area ID
- Incident type
- Priority score
- Severity
- Recommended action
- Operator summary
- Risk drivers

Emphasize that risk drivers make the score explainable for review and coordination.

## 6. Data-Source Readiness

Show the Data-Source Readiness panel. Explain that the listed layers indicate possible inputs for a future pilot, including partner integrations and future calibration needs.

## Phrases To Use

- Decision-priority support
- Operator review
- Revisit planning
- Alerting and response coordination
- Explainable risk drivers
- Complement existing monitoring systems

## Phrases To Avoid

- Predicts disasters with certainty
- Replaces GISTDA systems
- Final emergency-response decision
- Production-ready operational alerting
- Complete live GIS platform

