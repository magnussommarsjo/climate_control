import logging
from typing import NoReturn, Optional
import time
from datetime import datetime
from controller.data_central import get_data_from_url
from controller.storage import Storage

log = logging.getLogger(__name__)

class Sensor:
    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address
        self._data: dict = {}
        self.timestamp: Optional[datetime] = None
    
    def update(self) -> bool:
        """Update sensor with new values, returns True if succeed"""
        data = get_data_from_url(f"http://{self.address}/read/")
        if data is not None:
            self._data = data.get("external_temperature_sensor", {})
            self.timestamp = datetime.now()
            return True
        else:
            return False

    @property
    def temperature(self) -> float:
        return self._data.get("temperature", None)

    @property
    def humidity(self) -> float:
        return self._data.get("humidity", None)
    
    def to_dict(self) -> dict:
        return {
            f"{self.name}.temperature": self.temperature,
            f"{self.name}.humidity": self.humidity,
            f"{self.name}.timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        name=self.name
        address=self.address
        return f"{self.__class__.__name__}({name=}, {address=})"


def continious_logging(sensor: Sensor, storage: Storage, sample_time: int = 10) -> NoReturn:
    log.info(f"Continious logging started with sample time {sample_time}s")
    while True:
        if sensor.update():
            data = sensor.to_dict()
            storage.store(data)

        time.sleep(sample_time)

def main():
    sensor = Sensor(name="first_floor", address="192.168.1.21")
    
    print(sensor)
    sensor.update()
    print(sensor.to_dict())

if __name__ == "__main__":
    main()