from datetime import datetime

import pytest

from app.models.weather import WeatherData


def test_weather_model_initialization():
    data = {
        "sensor_id": "sensor_123",
        "temperature": 22.5,
        "humidity": 55.0,
        "wind_speed": 15.9,
        "pressure": 1013.0,
    }
    weather = WeatherData(**data)
    assert weather.sensor_id == "sensor_123"
    assert weather.temperature == 22.5
    assert weather.humidity == 55.0
    assert weather.wind_speed == 15.9
    assert weather.pressure == 1013.0
    assert isinstance(weather.timestamp, datetime)


@pytest.mark.parametrize(
    "field,value",
    [
        ("temperature", -60),  # out of range
        ("humidity", 150),  # out of range
        ("wind_speed", -1),  # out of range
        ("pressure", 700),  # out of range
    ],
)
def test_weather_model_invalid_input(field, value):
    data = {
        "sensor_id": "sensor_123",
        "temperature": 22.5,
        "humidity": 55.0,
        "wind_speed": 15.9,
        "pressure": 1013.0,
    }
    data[field] = value
    with pytest.raises(ValueError):
        WeatherData(**data)
