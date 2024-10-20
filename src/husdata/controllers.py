import logging
from typing import Any

from husdata.registers import ID_C30
import husdata.exceptions as exceptions
from husdata.gateway import H60
from husdata.util import clamp_value

log = logging.getLogger(__name__)


class Rego1000(H60):
    ID = ID_C30

    WRITABLE_VARS = {
        ID_C30.ROOM_TEMP_SETPOINT,
        ID_C30.ROOM_SENSOR_INFLUENCE,
        ID_C30.HEAT_SET_1_CURVE_L,
        ID_C30.HEAT_SET_1_CURVE_L_2,
        ID_C30.EXTRA_WARM_WATER,
        ID_C30.WARM_WATER_PROGRAM,
        ID_C30.EXTERNAL_CONTROL,
        ID_C30.EXTERNAL_CONTROL_2,
        ID_C30.OUTDOOR_TEMP_OFFSET,
        ID_C30.HEAT_SET_1_CURVE_L_2,
        ID_C30.HEAT_SET_2_CURVE_R_2,
        ID_C30.POOL_TEMP_SETPOINT,
    }

    async def set_variable(self, idx: str, value: Any) -> None:
        if idx not in self.WRITABLE_VARS:
            raise exceptions.NotWritableError(f"{idx} is a read-only variable.")

        if idx == ID_C30.OUTDOOR_TEMP_OFFSET:
            # Only accepts values  within range of -10 to 10 °C
            value = clamp_value(value, -10, 10)

        await super().set_variable(idx, value)

    @classmethod
    def translate_data(cls, data: dict) -> dict:
        return {id.name: data.get(id, None) for id in cls.ID}
