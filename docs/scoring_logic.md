# Scoring Logic

The MVP uses a transparent weighted formula:

```text
priority_score =
  0.40 * hazard_score
+ 0.30 * exposure_score
+ 0.20 * urgency_score
+ 0.10 * confidence
```

Each input score must be between `0.0` and `1.0`.

This formula is intentionally simple for demonstration and operator explainability. It is not a deterministic disaster prediction model and is not a final production formula.

## Severity Bands

| Priority Score | Severity |
| --- | --- |
| 0.00-0.34 | LOW |
| 0.35-0.54 | WATCH |
| 0.55-0.74 | MEDIUM |
| 0.75-0.89 | HIGH |
| 0.90-1.00 | CRITICAL |

## Recommended Actions

| Severity | Recommended Action |
| --- | --- |
| LOW | `MONITOR_ONLY` |
| WATCH | `KEEP_IN_MONITORING_QUEUE` |
| MEDIUM | `REVIEW_WITHIN_NEXT_OPERATIONAL_CYCLE` |
| HIGH | `PRIORITY_REVIEW_AND_COORDINATE_LOCAL_RESPONSE` |
| CRITICAL | `IMMEDIATE_REVIEW_AND_ESCALATION` |

