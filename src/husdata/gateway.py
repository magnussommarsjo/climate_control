import httpx
import json
from typing import Any, Optional
import logging
import husdata.exceptions as exceptions
from .registers import DataType, isDataType

log = logging.getLogger(__name__)

class H60:
    def __init__(self, address: str):
        """Instantiates an H60 unit

        Args:
            address: IP Address to H60
        """
        self.url = "http://" + address + "/api/"

    @staticmethod
    def _get_data_from_url(url: str) -> Optional[dict]:
        response = httpx.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    @staticmethod
    def _convert_raw_value(idx: str, value: str) -> Any:
        """Converts raw value from H60 to its proper data type

        Conversion based on H1 developer manual but modified to work with Rego 1000
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

    def toggle_bool(self, idx: str, state: Optional[bool] = None) -> None:
        """Toggles a boolean on or off

        Args:
            idx: Index to toggle
            state: Optional state to set True/False, otherwise toggles between states

        Raises:
            exceptions.TypeError: If Index is not an boolean
        """
        if not isDataType(idx, DataType.ON_OFF_BOOL):
            raise exceptions.TypeError(f"{idx} is not a boolean")

        data = self.get_all_data()
        value: bool = data[idx]

        if value == state:
            # Same state, no need do do anything
            return
        if value:
            self.set_variable(idx, "0")
        else:
            self.set_variable(idx, "1")

    def get_status(self) -> Optional[dict]:
        return self._get_data_from_url(self.url + "status")

    def get_all_data(self, convert: bool = True) -> Optional[dict]:
        data = self._get_data_from_url(self.url + "alldata")
        if convert:
            for idx, value in data.items():
                data[idx] = self._convert_raw_value(idx, value)
        return data

    def set_variable(self, idx: str, value: str) -> None:
        httpx.get(f"{self.url}set?idx={idx}&val={value}")
        log.info(f"Tried to set variable {idx} to {value}")
    
    def get_variable(self, idx: str) -> Any:
        data = self.get_all_data()
        return data[idx]
        