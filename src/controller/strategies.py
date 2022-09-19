from typing import Any, Callable, Optional
from husdata.controllers import Rego1000
import abc

# TODO:
# Should be able to trigger at certain time intervalls or specific times
# Remember state and history
# Use data from sensors and H60


class ControlStrategy:
    @abc.abstractmethod
    def trigger(self):
        """function to trigger at intervall"""
        raise NotImplementedError()

    @abc.abstractmethod
    def status(self) -> dict[str, Any]:
        """Method to deliver a status of the control strategy for easy overview and logging"""


class OffsetOutdoorTemperatureStrategy(ControlStrategy):
    """
    This compensates sensed outdoor temperature based on a indoor temperature setpoint
    and measured indoor temperature.
    """

    def __init__(
        self, rego: Rego1000, indoor_temperature_callable: Callable, influence: float
    ) -> None:
        self.rego = rego
        self.get_indoor_temperature = indoor_temperature_callable
        self.indoor_temperature: Optional[float] = None
        self.setpoint_temperature: Optional[float] = None
        self.influence = influence
        self.offset = 0.0

    def trigger(self):
        self.indoor_temperature = self.get_indoor_temperature()
        ID = self.rego.ID
        self.setpoint_temperature = self.rego.get_variable(ID.ROOM_TEMP_SETPOINT)
        self.offset = (
            self.indoor_temperature - self.setpoint_temperature
        ) * self.influence
        self.rego.set_variable(ID.OUTDOOR_TEMP_OFFSET, self.offset)

    def status(self) -> dict:
        return {
            "indoor_temperature": self.indoor_temperature,
            "setpoint_temperature": self.setpoint_temperature,
            "requested_offset": self.offset,
        }
