from dataclasses import dataclass
import os

@dataclass
class Config:
    # Application
    SAMPLE_TIME = os.getenv("SAMPLE_TIME", 60)
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = os.getenv("PORT", 80)

    # Husdata H60
    H60_ADDRESS = os.getenv("H60_ADDRESS", "192.168.1.12")
    
    # InfluxDB integration
    INFLUXDB_ADDRESS = os.getenv("INFLUXDB_ADDRESS", "influxdb2")
    INFLUXDB_PORT = os.getenv("INFLUXDB_PORT", 8086)
    INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")

def read_config() -> Config:
    return Config()