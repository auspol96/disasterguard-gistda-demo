# Roadmap

## MVP

- FastAPI scoring API
- Pydantic request and response models
- Transparent weighted scoring formula
- Severity and recommended action mapping
- Sample inputs and outputs for wildfire/haze, rapid flood, and landslide scenarios
- Pytest coverage for scoring and API behavior

## Next Iteration

- Add a small operator-facing dashboard
- Add source-specific connectors for approved upstream datasets
- Store scored incidents for review history
- Add geospatial metadata fields such as centroid, district, province, and observation time
- Add configurable scoring weights by incident type

## Future Considerations

- Calibrate scoring with domain experts and historical review outcomes
- Add audit trails for score inputs and operator decisions
- Support alert routing integrations
- Expand ASEAN demo scenarios while preserving explainability

