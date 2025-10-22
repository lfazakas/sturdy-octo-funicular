# Weather Data Service

A FastAPI-based service for receiving and querying weather data from various sensors. This service stores weather metrics in InfluxDB and provides a REST API for data ingestion and querying.

## Features

- **Data Ingestion**: Receive weather data from sensors via REST API
- **Data Querying**: Query weather data with flexible filters and aggregations
- **Metrics Support**: Temperature, humidity, wind speed, and atmospheric pressure
- **Statistical Operations**: Min, max, sum, and average calculations
- **Time Range Queries**: Query data within specified date ranges (1 day to 1 month)
- **Multi-Sensor Support**: Query data from specific sensors or all sensors
- **Docker Support**: Fully containerized with Docker Compose

## Technology Stack

- **Python 3.12+**
- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **InfluxDB 2.7** - Time-series database for storing weather metrics
- **Poetry** - Dependency management and packaging
- **Docker** - Containerization
- **Uvicorn** - ASGI server

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Using Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lfazakas/sturdy-octo-funicular
   cd sturdy-octo-funicular
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - InfluxDB UI: http://localhost:8086

## API Usage

### Submit Weather Data

Send weather data from a sensor:

```bash
curl -X POST "http://localhost:8000/api/v1/weather/data" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor-001",
    "temperature": 22.5,
    "humidity": 65.0,
    "wind_speed": 12.3,
    "pressure": 1013.25,
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Query Weather Data

Query weather data with various filters:

```bash
# Average temperature and humidity for sensor 1 in the last week
curl -X POST "http://localhost:8000/api/v1/weather/query" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_ids": ["sensor-001"],
    "metrics": ["temperature", "humidity"],
    "statistic": "average",
    "start_time": "2024-01-08T00:00:00Z",
    "end_time": "2024-01-15T00:00:00Z"
  }'
```

### Available Endpoints

- `POST /api/v1/weather/data` - Submit weather data
- `POST /api/v1/weather/query` - Query weather data
- `GET /api/v1/weather/sensors` - List available sensors
- `GET /api/v1/weather/metrics` - List available metrics
- `GET /api/v1/weather/statistics` - List available statistics
- `GET /health` - Health check
- `GET /` - Service information

## Data Models

### Weather Data Input

```json
{
  "sensor_id": "string",
  "temperature": 22.5,
  "humidity": 65.0,
  "wind_speed": 12.3,
  "pressure": 1013.25,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Query Parameters

```json
{
  "sensor_ids": ["sensor-001", "sensor-002"],
  "metrics": ["temperature", "humidity"],
  "statistic": "average",
  "start_time": "2024-01-08T00:00:00Z",
  "end_time": "2024-01-15T00:00:00Z"
}
```

## Configuration

The service can be configured using environment variables:

- `INFLUXDB_URL` - InfluxDB server URL (default: http://localhost:8086)
- `INFLUXDB_TOKEN` - InfluxDB authentication token
- `INFLUXDB_ORG` - InfluxDB organization (default: weather-org)
- `INFLUXDB_BUCKET` - InfluxDB bucket name (default: weather-data)

## Development

### Code Formatting

```bash
poetry run black app/
poetry run isort app/
```

### Linting

```bash
poetry run flake8 app/
poetry run mypy app/
```

## Project Structure

```
weather-data-service/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   └── routes.py           # API routes
│   ├── config/
│   │   └── settings.py         # Applicaton settings
│   ├── datastore/
│   │   └── influxdb_client.py  # InfluxDB operations
│   ├── models/
│   │   └── weather.py          # Pydantic models
│   └── service/
│       └── weather_service.py  # Service layer component
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── pyproject.toml              # Poetry configuration
└── README.md                   # This file
```