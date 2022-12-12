import abc
from datetime import datetime
from typing import Any, Callable, Optional, List
import time

from husdata.controllers import Rego1000

import logging

log = logging.getLogger(__name__)


class ControlStrategy(abc.ABC):
    """Abstract base class for defining a Control Strategy"""

    @abc.abstractmethod
    def trigger(self) -> None:
        """Method to trigger at interval"""
        raise NotImplementedError()

    @abc.abstractmethod
    def is_triggerable(self) -> bool:
        """If we can allow this strategy to be triggered"""
        raise NotImplementedError()

    @abc.abstractmethod
    def status(self) -> dict[str, Any]:
        """
        Method to deliver a status of the control strategy for easy overview and
        logging
        """
        raise NotImplementedError()
    
    def __str__(self):
        return f"{self.__class__.__name__}(...)"


class OffsetOutdoorTemperatureStrategy(ControlStrategy):
    """
    This compensates sensed outdoor temperature based on a indoor temperature set-point
    and measured indoor temperature.
    """

    def __init__(
        self, rego: Rego1000, indoor_temperature_callable: Callable, influence: float
    ) -> None:
        self.rego = rego
        self.get_indoor_temperature = indoor_temperature_callable
        self.influence: float = influence
        self.offset: float = 0.0
        self.indoor_temperature: Optional[float] = None
        self.setpoint_temperature: Optional[float] = None
        self.last_trigger: Optional[datetime] = None

    def trigger(self) -> None:
        self._update_temperatures()
        if self.setpoint_temperature is None:
            log.info("Could not find any setpoint value, set offset to 0")
            self.offset = 0

        elif self.indoor_temperature is None:
            log.info("Could not find any indoor temperature, set offset to 0")
            self.offset = 0
        else:
            self.offset = (
                self.indoor_temperature - self.setpoint_temperature
            ) * self.influence

        self.rego.set_variable(
            self.rego.ID.OUTDOOR_TEMP_OFFSET, round(self.offset * 10)
        )
        self.last_trigger = datetime.now()

    def _update_temperatures(self) ->  None:
        """Updates temperatuers needed for this strategy."""
        # Update temperatures
        self.indoor_temperature = self.get_indoor_temperature()
        setpoint_temperature = self.rego.get_variable(self.rego.ID.ROOM_TEMP_SETPOINT)
        if setpoint_temperature is not None:
            self.setpoint_temperature = setpoint_temperature
        else:
            log.info("Could not update setpoint temperature, uses old value")

    def is_triggerable(self) -> bool:
        if self.last_trigger is None:
            # Never triggered and therefore can safely run
            return True
        dt = datetime.now()
        if dt.hour > self.last_trigger.hour:
            return True
        elif dt.day != self.last_trigger.day:
            # date have changed so trigger
            return True

        return False

    def status(self) -> dict:
        return {
            "indoor_temperature": self.indoor_temperature,
            "setpoint_temperature": self.setpoint_temperature,
            "requested_offset": self.offset,
        }


class StrategyHandler:
    """Handles lifetime of strategy"""

    def __init__(self) -> None:
        self.strategies: List[ControlStrategy] = []
        self.is_running: bool = False

    def register_strategy(self, strategy: ControlStrategy) -> None:
        if not isinstance(strategy, ControlStrategy):
            raise TypeError(f"{strategy} not instance of {type(ControlStrategy)}")
        if strategy in self.strategies:
            log.info(f"Strategy {strategy} already registered")
            return

        log.info(f"Registered strategy: {strategy}")
        self.strategies.append(strategy)

    def unregister_strategy(self, strategy: ControlStrategy) -> None:
        if strategy in self.strategies:
            log.info(f"Removed strategy: {strategy}")
            self.strategies.remove(strategy)

    def stop_strategies(self):
        # TODO: Need to reset Rego to original state
        self.is_running = False

    def run_strategies(self):
        time.sleep(10)
        log.info(f"Strategies started")
        self.is_running = True
        while self.is_running:
            time.sleep(1)
            for strategy in self.strategies:
                if strategy.is_triggerable():
                    log.info(f"Strategy {strategy} triggered")
                    strategy.trigger()
