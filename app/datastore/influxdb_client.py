import logging
from typing import List

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from app.config import Settings
from app.models.weather import WeatherData, WeatherQuery, WeatherResponse

logger = logging.getLogger(__name__)


class InfluxDBDataStore:
    def __init__(self, app_settings: Settings):
        self.client: InfluxDBClient | None = None
        self.write_api = None
        self.query_api = None
        self.settings = app_settings

    async def initialize(self):
        """Initialize InfluxDB connection."""
        try:
            self.client = InfluxDBClient(
                url=self.settings.influxdb_url, token=self.settings.influxdb_token, org=self.settings.influxdb_org
            )

            self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.client.query_api()

            logger.info("InfluxDB connection initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB connection: {e}")
            raise

    async def write_weather_data(self, data: WeatherData) -> bool:
        assert self.write_api, "Write API not initialized"
        try:
            point = (
                Point("weather_metrics")
                .tag("sensor_id", data.sensor_id)
                .field("temperature", data.temperature)
                .field("humidity", data.humidity)
                .field("wind_speed", data.wind_speed)
                .field("pressure", data.pressure)
                .time(data.timestamp)
            )

            self.write_api.write(bucket=self.settings.influxdb_bucket, record=point)
            logger.info(f"Weather data written for sensor {data.sensor_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to write weather data: {e}")
            return False

    async def query_weather_data(self, query: WeatherQuery) -> WeatherResponse:
        assert self.query_api, "Query API not initialized"
        try:
            flux_query = self._build_flux_query(query)
            result = self.query_api.query(flux_query)
            return self._process_query_results(result, query)

        except Exception as e:
            logger.error(f"Failed to query weather data: {e}")
            return WeatherResponse(
                sensor_id=query.sensor_ids[0] if query.sensor_ids else "all",
                metrics=query.metrics,
                statistic=query.statistic,
                results=[],
            )

    async def get_all_sensor_ids(self) -> List[str]:
        assert self.query_api, "Query API not initialized"
        try:
            flux_query = f'from(bucket: "{self.settings.influxdb_bucket}")'
            flux_query += " |> range(start: -30d)"
            flux_query += ' |> filter(fn: (r) => r._measurement == "weather_metrics")'
            flux_query += ' |> keep(columns: ["sensor_id"]) |> distinct(column: "sensor_id")'
            result = self.query_api.query(flux_query)
            sensor_ids = [record.get_value() for table in result for record in table.records]
            return list(set(sensor_ids))

        except Exception as e:
            logger.error(f"Failed to query sensor IDs: {e}")
            return []

    def _build_flux_query(self, query: WeatherQuery) -> str:
        """Build Flux query string from query parameters."""
        # Base query
        flux_query = f'from(bucket: "{self.settings.influxdb_bucket}")'

        # Time range
        if query.start_time and query.end_time:
            flux_query += f" |> range(start: {query.start_time.isoformat()}, stop: {query.end_time.isoformat()})"
        else:
            # Default to last 24 hours if no time range specified
            flux_query += " |> range(start: -24h)"

        # Filter by measurement
        flux_query += ' |> filter(fn: (r) => r._measurement == "weather_metrics")'

        # Filter by sensor IDs
        if query.sensor_ids:
            sensor_filter = " or ".join([f'r.sensor_id == "{sensor_id}"' for sensor_id in query.sensor_ids])
            flux_query += f" |> filter(fn: (r) => {sensor_filter})"

        # Filter by fields (metrics)
        if query.metrics:
            field_filter = " or ".join([f'r._field == "{metric}"' for metric in query.metrics])
            flux_query += f" |> filter(fn: (r) => {field_filter})"

        # Group by sensor_id and _field
        flux_query += ' |> group(columns: ["sensor_id", "_field"])'

        # Apply aggregation based on statistic
        if query.statistic == "average":
            flux_query += " |> mean()"
        elif query.statistic == "min":
            flux_query += " |> min()"
        elif query.statistic == "max":
            flux_query += " |> max()"
        elif query.statistic == "sum":
            flux_query += " |> sum()"

        return flux_query

    def _process_query_results(self, result, query: WeatherQuery) -> WeatherResponse:
        results = []

        for table in result:
            for record in table.records:
                sensor_id = record.values.get("sensor_id", "unknown")
                field = record.values.get("_field", "unknown")
                value = record.values.get("_value", 0)

                results.append({"sensor_id": sensor_id, "metric": field, "value": value})

        return WeatherResponse(
            sensor_id=query.sensor_ids[0] if query.sensor_ids and len(query.sensor_ids) == 1 else "multiple",
            metrics=query.metrics,
            statistic=query.statistic,
            results=results,
        )

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("InfluxDB connection closed")
