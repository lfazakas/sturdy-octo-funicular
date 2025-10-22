from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import weather_router
from app.config import Settings
from app.datastore import InfluxDBDataStore
from app.service import WeatherService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings()  # type: ignore
    datastore = InfluxDBDataStore(app.state.settings)
    await datastore.initialize()
    app.state.weather_service = WeatherService(datastore)
    try:
        yield
    finally:
        await datastore.close()


app = FastAPI(
    title="Weather Data Service",
    description="A service for receiving and querying weather sensor data",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(weather_router, prefix="/api/v1", tags=["weather"])


@app.get("/")
async def root():
    return {"message": "Weather Data Service", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
