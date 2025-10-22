from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.weather import ErrorResponse, WeatherData, WeatherDataResponse, WeatherQuery, WeatherResponse
from app.service import WeatherService

weather_router = APIRouter()


async def get_weather_service(request: Request) -> WeatherService:
    service: WeatherService | None = getattr(request.app.state, "weather_service", None)
    if not service:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Weather service not available")
    return service


@weather_router.post(
    "/weather/data",
    response_model=WeatherDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit weather data",
    description="Submit new weather data from a sensor",
)
async def submit_weather_data(
    data: WeatherData,
    service: WeatherService = Depends(get_weather_service),
):
    try:
        success = await service.store_weather_data(data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store weather data"
            )

        return WeatherDataResponse(
            message="Weather data stored successfully", sensor_id=data.sensor_id, timestamp=data.timestamp
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error storing weather data: {str(e)}"
        )


@weather_router.post(
    "/weather/query",
    response_model=WeatherResponse,
    summary="Query weather data",
    description="Query weather data with specified filters and aggregations",
)
async def query_weather(
    query: WeatherQuery,
    service: WeatherService = Depends(get_weather_service),
):
    """
    Query weather data based on specified criteria (sensor IDs, metrics, date range)
    """
    try:
        return await service.query_weather_data(query)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error querying weather data: {str(e)}"
        )


@weather_router.get(
    "/weather/sensors",
    response_model=List[str],
    summary="List available sensors",
    description="Get a list of all sensor IDs that have submitted data",
)
async def list_sensors(
    service: WeatherService = Depends(get_weather_service),
):
    try:
        return await service.get_available_sensors()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving sensor list: {str(e)}"
        )


@weather_router.get(
    "/weather/metrics",
    response_model=List[str],
    summary="List available metrics",
    description="Get a list of all available weather metrics",
)
async def list_metrics(
    service: WeatherService = Depends(get_weather_service),
):
    return service.get_available_metrics()


@weather_router.get(
    "/weather/statistics",
    response_model=List[str],
    summary="List available statistics",
    description="Get a list of all available statistical operations",
)
async def list_statistics(
    service: WeatherService = Depends(get_weather_service),
):
    return service.get_available_statistics()
