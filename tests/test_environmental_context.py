from app import environmental_context
from app.environmental_context import get_environmental_context_for_area, load_environmental_context_samples


def test_environmental_context_loading(tmp_path):
    config_path = tmp_path / "environmental_context_samples.json"
    config_path.write_text(
        """
        {
          "areas": {
            "AREA-001": {
              "temperature_c": 34,
              "humidity_percent": 35,
              "wind_speed_kph": 12,
              "wind_direction": "SW",
              "rain_probability_percent": 10,
              "pm25_ugm3": 42.5
            }
          }
        }
        """,
        encoding="utf-8",
    )

    loaded = load_environmental_context_samples(config_path)
    area_context = get_environmental_context_for_area("AREA-001", config_path)

    assert loaded["AREA-001"]["temperature_c"] == 34
    assert area_context["pm25_ugm3"] == 42.5
    assert area_context["source"] == "sample"
    assert get_environmental_context_for_area("MISSING", config_path) == {}


def test_environmental_context_loading_direct_area_mapping(tmp_path):
    config_path = tmp_path / "environmental_context_samples.json"
    config_path.write_text(
        """
        {
          "NTH-CHIANGDAO-MUEANGNA-001": {
            "temperature_c": 34.2,
            "humidity_percent": 34,
            "wind_speed_kph": 12,
            "wind_direction": "SW",
            "rain_probability_percent": 10,
            "pm25_ugm3": 42.5
          }
        }
        """,
        encoding="utf-8",
    )

    area_context = get_environmental_context_for_area(
        "NTH-CHIANGDAO-MUEANGNA-001",
        config_path,
    )

    assert area_context["temperature_c"] == 34.2


def test_environmental_context_uses_live_open_meteo_when_available(monkeypatch, tmp_path):
    config_path = tmp_path / "environmental_context_samples.json"
    config_path.write_text('{"AREA-001": {"temperature_c": 30}}', encoding="utf-8")
    monkeypatch.setattr(
        environmental_context,
        "fetch_open_meteo_environment",
        lambda lat, lon: {"status": "ok", "source": "open-meteo", "temperature_c": 35},
    )

    area_context = get_environmental_context_for_area("AREA-001", config_path, lat=1.0, lon=2.0)

    assert area_context["source"] == "open-meteo"
    assert area_context["temperature_c"] == 35


def test_environmental_context_falls_back_to_sample_when_live_fails(monkeypatch, tmp_path):
    config_path = tmp_path / "environmental_context_samples.json"
    config_path.write_text('{"AREA-001": {"temperature_c": 30}}', encoding="utf-8")
    monkeypatch.setattr(
        environmental_context,
        "fetch_open_meteo_environment",
        lambda lat, lon: {"status": "error", "message": "network failed"},
    )

    area_context = get_environmental_context_for_area("AREA-001", config_path, lat=1.0, lon=2.0)

    assert area_context["source"] == "sample"
    assert area_context["temperature_c"] == 30
