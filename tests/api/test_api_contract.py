from fastapi.testclient import TestClient

from app.main import app


class MockWeatherService:
    async def store_weather_data(self, data):
        return True


def test_weather_data_post_happy_path(monkeypatch):
    client = TestClient(app)

    from app.api.routes import get_weather_service

    app.dependency_overrides[get_weather_service] = lambda: MockWeatherService()

    payload = {"sensor_id": "sensor_abc", "temperature": 23.5, "humidity": 32, "wind_speed": 10.2, "pressure": 1009}
    resp = client.post("/api/v1/weather/data", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["sensor_id"] == payload["sensor_id"]
    assert body["message"] == "Weather data stored successfully"
    assert "timestamp" in body


def test_weather_post_validation_error():
    client = TestClient(app)

    from app.api.routes import get_weather_service

    app.dependency_overrides[get_weather_service] = lambda: MockWeatherService()

    payload = {
        "sensor_id": "sensor_abc",
        # missing temperature
        "humidity": 32,
        "wind_speed": 10.2,
        "pressure": 1009,
    }
    resp = client.post("/api/v1/weather/data", json=payload)
    assert resp.status_code == 422
    assert "temperature" in resp.text
