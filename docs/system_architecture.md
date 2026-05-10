# System Architecture

DisasterGuard is a lightweight FastAPI demo for a multi-sensor disaster-priority intelligence layer. It is designed to sit above existing monitoring systems and help rank which geolocated areas deserve earlier review, revisit, alerting, or response coordination.

```text
Existing monitoring systems and data sources
        |
        v
Multi-source data connector
        |
        v
Hazard, exposure, urgency, and confidence inputs
        |
        v
Transparent priority scoring engine
        |
        v
Severity and recommended action mapping
        |
        v
API response for operators, dashboards, or alert workflows
```

The MVP exposes:

- `GET /api/health`
- `POST /api/incident/score`

This demo does not replace GISTDA systems or other disaster-monitoring platforms. It provides a compact decision-support output that can complement upstream data sources.

