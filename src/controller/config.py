"""Configuration parameters

This module contains a data structre and method for reading environment variables. 
"""
import logging

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Config(BaseSettings):
    SAMPLE_TIME: int = 60
    HOST: str = "0.0.0.0"
    PORT: int = 80
    H60_ADDRESS: str
    MQTT_HOST: str
    MQTT_PORT: int = 1883
    MQTT_CLIENT_ID: str = "controller.climate_control"


    model_config = ConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra="allow"
    )


def read_config(**kwargs) -> Config:
    """Read configuration parameters and environment variables

    **kwargs:
        key word arguments will override existing environment variables

    Returns:
        Config: _description_
    """
    config = Config(**kwargs)
    logger.info(f"Initiated config: {config}")
    return config
