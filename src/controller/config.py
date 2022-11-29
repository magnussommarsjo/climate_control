"""Configuration parameters

This module contains a data structre and method for reading environment variables. 
"""

from typing import Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    SAMPLE_TIME: int = 60
    HOST: str = "0.0.0.0"
    PORT: int = 80
    H60_ADDRESS: str
    INFLUXDB_ADDRESS: str = "influxdb2"
    INFLUXDB_PORT: int = 8086
    INFLUXDB_TOKEN: Optional[str]
    MQTT_HOST: str
    MQTT_PORT: int = 1883
    MQTT_CLIENT_ID: str = "controller.climate_control"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def read_config(**kwargs) -> Config:
    """Read configuration parameters and environment variables

    **kwargs:
        key word arguments will override existing environment variables

    Returns:
        Config: _description_
    """
    return Config(**kwargs)
