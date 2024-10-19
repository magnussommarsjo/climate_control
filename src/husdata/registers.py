import enum
from typing import Iterable

from .exceptions import TranslationError


@enum.unique
class DataType(str, enum.Enum):
    """Identifier of Data type via the first integer in the register ID

    Reference:
    https://varmepump.one/docs/h60-manual/for-advanced-users/h1-development-guide/#registers
    """

    DEGREES = "0"
    ON_OFF_BOOL = "1"
    NUMBER = "2B"
    PERCENT = "3"
    AMPERE = "4"
    KWH = "5"
    HOURS = "6"
    MINUTES = "7"
    DEGREE_MINUTES = "8"
    KW = "9"

def is_data_type(idx: str, data_type: DataType) -> bool:
    """Checks if a index is a acertain DataType"""
    try:
        return  idx[0] in data_type
    except IndexError as e:
        raise TranslationError(f"Could not identify data type of {idx}")
def is_in_data_types(idx: str, data_types: Iterable[DataType]) -> bool:
    return any(is_data_type(idx, data_type) for data_type in data_types)

@enum.unique
class ID_C30(enum.StrEnum):
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
    HOLLIDAY_MODE = "1210"
    SUMMER_MODE = "B20A"
    WARM_WATER_PROGRAM = "2213"
    EXTERNAL_CONTROL = "2233"
    EXTERNAL_CONTROL_2 = "2234"
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
