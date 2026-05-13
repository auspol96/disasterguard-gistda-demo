from app.connectors import open_meteo_environment


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_fetch_open_meteo_environment_normalizes_weather_and_air_quality(monkeypatch):
    responses = [
        FakeResponse(
            {
                "current": {
                    "temperature_2m": 34.5,
                    "relative_humidity_2m": 35,
                    "wind_speed_10m": 12.4,
                    "wind_direction_10m": 225,
                },
                "hourly": {"precipitation_probability": [20]},
            }
        ),
        FakeResponse({"current": {"pm2_5": 42.7}}),
    ]

    monkeypatch.setattr(
        open_meteo_environment.requests,
        "get",
        lambda *args, **kwargs: responses.pop(0),
    )

    result = open_meteo_environment.fetch_open_meteo_environment(19.57651, 99.01361)

    assert result["status"] == "ok"
    assert result["source"] == "open-meteo"
    assert result["temperature_c"] == 34.5
    assert result["humidity_percent"] == 35
    assert result["wind_speed_kph"] == 12.4
    assert result["wind_direction"] == "SW"
    assert result["wind_direction_degrees"] == 225
    assert result["rain_probability_percent"] == 20
    assert result["pm25_ugm3"] == 42.7
    assert result["fetched_at"]


def test_wind_degrees_to_compass():
    assert open_meteo_environment.wind_degrees_to_compass(0) == "N"
    assert open_meteo_environment.wind_degrees_to_compass(45) == "NE"
    assert open_meteo_environment.wind_degrees_to_compass(90) == "E"
    assert open_meteo_environment.wind_degrees_to_compass(225) == "SW"
