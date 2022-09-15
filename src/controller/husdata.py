import enum
import json
import logging
from typing import Any
import httpx

log = logging.getLogger(__name__)


@enum.unique
class ID_C30(str, enum.Enum):
    """Indexes for IVT Rego 1000 Controller and Bosh Pro Control 500 Controller

    Reference:
        https://online.husdata.se/h-docs/C30.pdf
    """

    RADIATOR_FORWARD = "0002"
    HEAT_CARRIER_RETURN = "0003"
    HEAT_CARRIER_FORWARD = "0004"
    BRINE_IN_EVAPORATOR = "0005"
    BRINE_OUT_CONDENSER = "0006"
    OUTDOOR = "0007"
    INDOOR = "0008"
    WARM_WATER_1_TOP = "0009"
    HOT_GAS_COMPRESSOR = "000B"
    AIR_INTAKE = "000E"
    POOL = "0011"
    INDOOR_2 = "0021"
    COMPRESSOR = "1A01"
    PUMP_COLD_CIRCUIT = "1A04"
    PUMP_HEAT_CIRCUIT = "1A05"
    PUMP_RADIATOR = "1A06"
    SWITCH_VALVE_1 = "1A07"
    SWITCH_VALVE_2 = "1A08"
    FAN = "1A09"
    HIGH_PRESSOSTAT = "1A0A"
    LOW_PRESSOSTAT = "1A0B"
    HEATING_CABLE = "1A0C"
    CRANK_CASE_HEATER = "1A0D"
    ADD_HEAT_STATUS = "3104"
    WARM_WATER_SETPOINT = "0111"
    HEATING_SETPOINT = "0107"
    ALARM = "1A20"
    PUMP_RADIATOR_2 = "1A21"
    # Write variables
    ROOM_TEMP_SETPOINT = "0203"
    ROOM_SENSOR_INFLUENCE = "2204"
    HEAT_SET_1_CURVE_L = "0205"
    HEAT_SET_2_CURVE_R = "0206"
    EXTRA_WARM_WATER = "6209"
    WARM_WATER_PROGRAM = "2213"
    EXTERNAL_CONTROL = "2233"
    EXTERNAl_CONTROL_2 = "2234"
    OUTDOOR_TEMP_OFFSET = "0217"
    HEAT_SET_1_CURVE_L_2 = "0222"
    HEAT_SET_2_CURVE_R_2 = "0223"
    POOL_TEMP_SETPOINT = "0219"
    # Energy consumptions
    SUPP_ENERGY_HEATING = "5C52"
    SUPP_ENERGY_HOTWATER = "5C53"
    COMPR_CONS_HEATING = "5C55"
    COMPR_CONS_HOTWATER = "5C56"
    AUX_CONS_HEATING = "5C58"
    AUX_CONS_HOTWATER = "5C59"
    # Versions
    PROG_VER_MAJOR = "2F00"
    PROG_VER_MINOR = "2F01"
    PROG_VER_REVISION = "2F02"


@enum.unique
class DataType(int, enum.Enum):
    """Identifier of Data type via the first integer in the register ID

    Reference:
    https://varmepump.one/docs/h60-manual/for-advanced-users/h1-development-guide/#registers
    """

    DEGREES = 0
    ON_OFF_BOOL = 1
    NUMBER = 2
    PERCENT = 3
    AMPERE = 4
    KWH = 5
    HOURS = 6
    MINUTES = 7
    DEGREE_MINUTES = 8
    KW = 9


def print_data(data: dict, ID: enum.Enum) -> None:
    """Prints translated data if exist

    Args:
        data: Raw data returned from request as a dictionary
        ID: Index registry for your controller as  a registry
    """
    for id in ID:
        print(id.name, ":", data.get(id, None))


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

        Args:
            idx: Index of the variable
            value: Raw value from H60 request response
        """
        if value is None:
            return None

        no = int(idx[0])
        if no in {
            DataType.DEGREES,
            DataType.NUMBER,
            DataType.PERCENT,
            DataType.AMPERE,
            DataType.KWH,
        }:
            value = float(value) / 10
        elif no == DataType.ON_OFF_BOOL:
            value = bool(int(value))
        elif no in {
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


def main():
    h60 = H60("192.168.1.12")
    print_data(h60.get_all_data(), ID_C30)
    # h60.set_variable(ID_C30.ROOM_TEMP_SETPOINT, "200")


if __name__ == "__main__":
    main()
