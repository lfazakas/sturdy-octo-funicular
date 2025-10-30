from unittest.mock import AsyncMock

import pytest

from app.models.weather import WeatherData, WeatherQuery, WeatherResponse
from app.service.weather_service import WeatherService


@pytest.mark.asyncio
async def test_store_weather_data_success():

    mock_db = AsyncMock()
    mock_db.write_weather_data.return_value = True
    service = WeatherService(mock_db)
    data = WeatherData(sensor_id="sensor_1", temperature=20.5, humidity=60.0, wind_speed=10.1, pressure=1000.0)

    result = await service.store_weather_data(data)

    assert result is True
    mock_db.write_weather_data.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_query_weather_data_success():

    mock_db = AsyncMock()
    fake_response = WeatherResponse(
        sensor_id="sensor_1",
        metrics=["temperature"],
        statistic="average",
        results=[{"sensor_id": "sensor_1", "metric": "temperature", "value": 20.0}],
    )
    mock_db.query_weather_data.return_value = fake_response
    service = WeatherService(mock_db)
    query = WeatherQuery(sensor_ids=["sensor_1"], metrics=["temperature"], statistic="average")

    response = await service.query_weather_data(query)

    assert response.sensor_id == "sensor_1"
    assert response.metrics == ["temperature"]
    assert response.statistic == "average"
    assert response.results == [{"sensor_id": "sensor_1", "metric": "temperature", "value": 20.0}]
    mock_db.query_weather_data.assert_awaited_once_with(query)
