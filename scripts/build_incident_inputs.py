import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA_DIR = ROOT / "sample_data"
SAMPLE_INPUTS_DIR = ROOT / "sample_inputs"


def clamp(value):
    return max(0.0, min(1.0, round(value, 2)))


def average(*values):
    return clamp(sum(values) / len(values))


def read_csv_by_area(filename):
    with (SAMPLE_DATA_DIR / filename).open(newline="", encoding="utf-8") as handle:
        return {row["area_id"]: row for row in csv.DictReader(handle)}


def number(row, key):
    return float(row[key])


def write_json(filename, payload):
    SAMPLE_INPUTS_DIR.mkdir(exist_ok=True)
    path = SAMPLE_INPUTS_DIR / filename
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_wildfire(wildfire, rainfall, terrain, vegetation):
    area_id = "NTH-CHIANGMAI-001"
    fire = wildfire[area_id]
    rain = rainfall[area_id]
    terrain_row = terrain[area_id]
    veg = vegetation[area_id]
    return {
        "area_id": area_id,
        "incident_type": "wildfire_haze",
        "hazard_score": average(
            number(fire, "hotspot_cluster_score"),
            number(fire, "hotspot_age_score"),
            number(veg, "vegetation_stress_score"),
            number(veg, "dryness_score"),
        ),
        "exposure_score": average(
            number(terrain_row, "community_exposure_score"),
            number(terrain_row, "road_infrastructure_score"),
        ),
        "urgency_score": average(
            number(fire, "wind_spread_score"),
            number(veg, "humidity_temperature_wind_score"),
        ),
        "confidence": average(
            number(fire, "hotspot_cluster_score"),
            number(veg, "vegetation_stress_score"),
            1 - number(rain, "rainfall_accumulation_score"),
        ),
        "risk_drivers": [
            fire["risk_driver"],
            veg["risk_driver"],
            "dryness signal",
            "wind spread potential",
            terrain_row["risk_driver"],
        ],
    }


def build_flood(rainfall, terrain):
    area_id = "NTH-CHIANGRAI-002"
    rain = rainfall[area_id]
    terrain_row = terrain[area_id]
    return {
        "area_id": area_id,
        "incident_type": "rapid_flood",
        "hazard_score": average(
            number(rain, "rainfall_accumulation_score"),
            number(rain, "rainfall_intensity_score"),
            number(terrain_row, "river_proximity_score"),
        ),
        "exposure_score": average(
            number(terrain_row, "community_exposure_score"),
            number(terrain_row, "road_infrastructure_score"),
        ),
        "urgency_score": average(
            number(rain, "rainfall_intensity_score"),
            number(rain, "soil_saturation_score"),
            number(terrain_row, "river_proximity_score"),
        ),
        "confidence": average(
            number(rain, "rainfall_accumulation_score"),
            number(rain, "rainfall_intensity_score"),
            number(terrain_row, "river_proximity_score"),
        ),
        "risk_drivers": [
            rain["risk_driver"],
            "rainfall intensity increase",
            "river proximity",
            "low-lying terrain proxy",
            terrain_row["risk_driver"],
        ],
    }


def build_landslide(rainfall, terrain, vegetation):
    area_id = "NTH-MAEHONGSON-003"
    rain = rainfall[area_id]
    terrain_row = terrain[area_id]
    veg = vegetation[area_id]
    return {
        "area_id": area_id,
        "incident_type": "landslide",
        "hazard_score": average(
            number(rain, "rainfall_accumulation_score"),
            number(rain, "soil_saturation_score"),
            number(terrain_row, "slope_score"),
        ),
        "exposure_score": average(
            number(terrain_row, "community_exposure_score"),
            number(terrain_row, "road_infrastructure_score"),
        ),
        "urgency_score": average(
            number(rain, "rainfall_intensity_score"),
            number(terrain_row, "slope_score"),
            number(rain, "soil_saturation_score"),
        ),
        "confidence": average(
            number(rain, "rainfall_accumulation_score"),
            number(terrain_row, "slope_score"),
            number(veg, "vegetation_stress_score"),
        ),
        "risk_drivers": [
            rain["risk_driver"],
            "steep slope",
            "soil saturation proxy",
            veg["risk_driver"],
            terrain_row["risk_driver"],
        ],
    }


def build_incident_inputs():
    wildfire = read_csv_by_area("wildfire_hotspots_sample.csv")
    rainfall = read_csv_by_area("rainfall_sample.csv")
    terrain = read_csv_by_area("terrain_exposure_sample.csv")
    vegetation = read_csv_by_area("vegetation_stress_sample.csv")

    generated = {
        "generated_wildfire_haze_chiangmai.json": build_wildfire(
            wildfire, rainfall, terrain, vegetation
        ),
        "generated_rapid_flood_chiangrai.json": build_flood(rainfall, terrain),
        "generated_landslide_maehongson.json": build_landslide(
            rainfall, terrain, vegetation
        ),
    }

    for filename, payload in generated.items():
        write_json(filename, payload)
    return generated


if __name__ == "__main__":
    for filename in build_incident_inputs():
        print(f"wrote sample_inputs/{filename}")
