from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # InfluxDB settings
    influxdb_url: str
    influxdb_token: str
    influxdb_org: str
    influxdb_bucket: str

    class Config:
        case_sensitive = False
