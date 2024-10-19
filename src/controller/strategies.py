import asyncio
from datetime import datetime
from typing import NoReturn, Optional

from controller.mqtt import MQTTSensor
from husdata.controllers import Rego1000

import logging

log = logging.getLogger(__name__)


class OffsetOutdoorTemperatureStrategy():
    """
    This compensates sensed outdoor temperature based on a indoor temperature set-point
    and measured indoor temperature.
    """

    def __init__(
        self,
        rego: Rego1000,
        temperature_sensor: MQTTSensor,
        influence: float,
        period: int = 3600,
    ) -> None:
        self._rego = rego
        self._temperature_sensor = temperature_sensor
        self.influence: float = influence
        self.temperature_offest: float = 0.0
        self.temperature_indoor: Optional[float] = None
        self.temperature_setpoint: Optional[float] = None
        self.last_trigger: Optional[datetime] = None
        self.period = period

    async def trigger(self) -> None:
        self._update_temperatures()
        log.info(f"Triggered with {self.temperature_indoor=}, {self.temperature_setpoint=}, {self.temperature_offest=}")
        if self.temperature_setpoint is None:
            log.info("Could not find any setpoint value, set offset to 0")
            self.temperature_offest = 0

        elif self.temperature_indoor is None:
            log.info("Could not find any indoor temperature, set offset to 0")
            self.temperature_offest = 0
        else:
            self.temperature_offest = (
                self.temperature_indoor - self.temperature_setpoint
            ) * self.influence

        await self._rego.set_variable(
            self._rego.ID.OUTDOOR_TEMP_OFFSET, self.temperature_offest
        )
        self.last_trigger = datetime.now()

    def _update_temperatures(self) -> None:
        """Updates temperatuers needed for this strategy."""
        self.temperature_indoor = self._temperature_sensor.value
        setpoint_temperature = self._rego.get_variable(self._rego.ID.ROOM_TEMP_SETPOINT)
        if setpoint_temperature is not None:
            self.temperature_setpoint = setpoint_temperature
        else:
            log.info("Could not update setpoint temperature, uses old value")

    async def start(self) -> NoReturn:
        while True:
            await self.trigger()
            await asyncio.sleep(self.period)
