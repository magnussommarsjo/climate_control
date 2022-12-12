import json
import logging
from typing import Callable, NoReturn, Optional
import time
from datetime import datetime

import httpx

from controller.storage import Storage

log = logging.getLogger(__name__)


def get_data_from_url(url: str) -> dict:
    """
    Returns a dictionary of the url data or None if the url is not valid or error
    occurred.
    """
    try:
        response = httpx.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None
    except httpx.RequestError as e:
        log.error(f"An error occurred while requesting {e.request.url!r}")
        return None


class Sensor:
    """Custom Pico W sensor

    Class for handling the custom built Pico W sensor
    """

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
            f"{self.name}.timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        name = self.name
        address = self.address
        return f"{self.__class__.__name__}({name=}, {address=})"




def continuous_logging(
    logging_function: Callable[[], dict], storage: Storage, sample_time: int = 10
) -> NoReturn:
    """Continuous logging of data returned by the callable function

    Args:
        logging_function: Function to call for getting data to log
        storage: Object to store data to.
        sample_time: Sample time of logging Defaults to 10.

    Returns:
        NoReturn: Keeps on until process/thread is killed
    """
    time.sleep(20)
    log.info(f"Continuous logging started with sample time {sample_time}s")
    while True:
        data = logging_function()
        if data:
            storage.store(data)

        time.sleep(sample_time)


def main():
    """Small test of reading from Sensor class"""
    
    sensor = Sensor(name="first_floor", address="192.168.1.21")
    print(sensor)
    sensor.update()
    print(sensor.to_dict())


if __name__ == "__main__":
    main()
