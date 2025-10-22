from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class WeatherData(BaseModel):
    """Model for incoming weather data from sensors."""

    sensor_id: str = Field(..., description="Unique identifier for the sensor")
    temperature: float = Field(..., description="Temperature in Celsius", ge=-50, le=60)
    humidity: float = Field(..., description="Humidity percentage", ge=0, le=100)
    wind_speed: float = Field(..., description="Wind speed in km/h", ge=0, le=300)
    pressure: float = Field(..., description="Atmospheric pressure in hPa", ge=800, le=1200)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the measurement"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WeatherQuery(BaseModel):
    """Model for weather data queries."""

    sensor_ids: List[str] | None = Field(None, description="List of sensor IDs to query (empty means all sensors)")
    metrics: List[str] = Field(
        ..., description="List of metrics to retrieve (temperature, humidity, wind_speed, pressure)"
    )
    statistic: Literal["min", "max", "sum", "average"] = Field(..., description="Statistical operation to apply")
    start_time: datetime | None = Field(None, description="Start time for the query range")
    end_time: datetime | None = Field(None, description="End time for the query range")

    @field_validator("metrics")
    def validate_metrics(cls, v: List[str]):
        """Validate that metrics are from allowed list."""
        allowed_metrics = ["temperature", "humidity", "wind_speed", "pressure"]
        for metric in v:
            if metric not in allowed_metrics:
                raise ValueError(f"Invalid metric: {metric}. Allowed metrics: {allowed_metrics}")
        return v

    @field_validator("end_time")
    def validate_time_range(cls, v: datetime | None, info: FieldValidationInfo):
        """Validate that end_time is after start_time."""
        start_time = info.data.get("start_time")
        if v and start_time and v <= start_time:
            raise ValueError("end_time must be after start_time")
        return v


class WeatherResponse(BaseModel):
    """Model for weather data query responses."""

    sensor_id: str = Field(..., description="Sensor ID or 'multiple' for multiple sensors")
    metrics: List[str] = Field(..., description="Requested metrics")
    statistic: str = Field(..., description="Applied statistical operation")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    query_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Time when query was executed"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WeatherDataResponse(BaseModel):
    """Response model for successful weather data ingestion."""

    message: str = Field(..., description="Success message")
    sensor_id: str = Field(..., description="Sensor ID")
    timestamp: datetime = Field(..., description="Timestamp of the data")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the error"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
