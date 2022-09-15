import httpx
import json
from typing import Any
import logging
from .registers import DataType

log = logging.getLogger(__name__)

class H60:
    def __init__(self, address: str):
        """Instantiates an H60 unit

        Args:
            address: IP Address to H60
        """
        self.url = "http://" + address + "/api/"

    @staticmethod
    def _get_data_from_url(url: str) -> dict:
        response = httpx.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    @staticmethod
    def _convert_raw(idx: str, value: str) -> Any:
        """Converts raw value from H60 to its propper data type

        Convcersion based on H1 developer manual but modified to work with Regoo 1000
        IVT Greenline

        Args:
            idx: Index of the variable
            value: Raw value from H60 request response
        """
        if value is None:
            return None

        no = int(idx[0])
        if no in {
            DataType.DEGREES,
            DataType.PERCENT,
            DataType.AMPERE,
        }:
            value = float(value) / 10
        elif no in {
            DataType.KWH,
        }:
            value = float(value) / 100
        elif no == DataType.ON_OFF_BOOL:
            value = bool(int(value))
        elif no in {
            DataType.NUMBER,
            DataType.HOURS,
            DataType.MINUTES,
            DataType.DEGREE_MINUTES,
            DataType.KW,
        }:
            value = int(value)
        else:
            raise ValueError(f"Could not identify data type of {idx}")
        return value

    def get_status(self) -> dict:
        return self._get_data_from_url(self.url + "status")

    def get_all_data(self) -> dict:
        data = self._get_data_from_url(self.url + "alldata")
        for idx, value in data.items():
            data[idx] = self._convert_raw(idx, value)
        return data

    def set_variable(self, idx: str, value: str) -> None:
        httpx.get(f"{self.url}set?idx={idx}&val={value}")
        log.info(f"Tried to set variable {idx} to {value}")
        