import logging
from datetime import datetime, timedelta, timezone
from typing import List

from app.datastore import InfluxDBDataStore
from app.models.weather import WeatherData, WeatherQuery, WeatherResponse

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self, datastore: InfluxDBDataStore):
        self.datastore = datastore

    async def store_weather_data(self, data: WeatherData) -> bool:
        try:
            if not self._validate_data_quality(data):
                logger.warning(f"Data quality validation failed for sensor {data.sensor_id}")
                return False

            success = await self.datastore.write_weather_data(data)

            if success:
                logger.info(f"Weather data stored successfully for sensor {data.sensor_id}")
            else:
                logger.error(f"Failed to store weather data for sensor {data.sensor_id}")

            return success

        except Exception as e:
            logger.error(f"Error storing weather data: {e}")
            return False

    async def query_weather_data(self, query: WeatherQuery) -> WeatherResponse:
        try:
            result = await self.datastore.query_weather_data(query)

            logger.info(f"Weather query executed successfully for {len(result.results)} results")
            return result

        except Exception as e:
            logger.error(f"Error querying weather data: {e}")
            return WeatherResponse(
                sensor_id=query.sensor_ids[0] if query.sensor_ids else "all",
                metrics=query.metrics,
                statistic=query.statistic,
                results=[],
            )

    async def get_available_sensors(self) -> List[str]:
        try:
            result = await self.datastore.get_all_sensor_ids()
            logger.info("Get sensors query executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error querying sensor ids: {e}")
            return []

    def get_available_metrics(self) -> List[str]:
        return ["temperature", "humidity", "wind_speed", "pressure"]

    def get_available_statistics(self) -> List[str]:
        return ["min", "max", "sum", "average"]

    def _validate_data_quality(self, data: WeatherData) -> bool:
        if data.timestamp > datetime.now(timezone.utc) + timedelta(minutes=5):
            logger.warning(f"Timestamp too far in the future: {data.timestamp}")
            return False

        return True
