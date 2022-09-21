import abc
from datetime import datetime
from typing import Any, Callable, Optional, List
from husdata.controllers import Rego1000
import time

import logging

log = logging.getLogger(__name__)

# TODO:
# Should be able to trigger at certain time intervalls or specific times
# Remember state and history
# Use data from sensors and H60


class ControlStrategy:
    @abc.abstractmethod
    def trigger(self) -> None:
        """function to trigger at intervall"""
        raise NotImplementedError()

    @abc.abstractmethod
    def is_triggerable(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def status(self) -> dict[str, Any]:
        """Method to deliver a status of the control strategy for easy overview and logging"""
        raise NotImplementedError()


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
        self.influence = influence
        self.offset = 0.0
        self.indoor_temperature: Optional[float] = None
        self.setpoint_temperature: Optional[float] = None
        self.last_trigger: Optional[datetime] = None

    def trigger(self) -> None:
        self.indoor_temperature = self.get_indoor_temperature()
        ID = self.rego.ID
        self.setpoint_temperature = self.rego.get_variable(ID.ROOM_TEMP_SETPOINT)
        self.offset = (
            self.indoor_temperature - self.setpoint_temperature
        ) * self.influence
        self.rego.set_variable(ID.OUTDOOR_TEMP_OFFSET, round(self.offset*10))
        self.last_trigger = datetime.now()

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
    def __init__(self) -> None:
        self.strategies: List[ControlStrategy] = []
        self.is_running: bool = False

    def register_strategy(self, strategy: ControlStrategy) -> None:
        if not isinstance(strategy, ControlStrategy):
            raise TypeError(f"{strategy} not instance of {type(ControlStrategy)}")
        if strategy in self.strategies:
            log.info(f"Strategy {strategy} already registered")
            return

        self.strategies.append(strategy)

    def unregister_strategy(self, strategy: ControlStrategy) -> None:
        if strategy in self.strategies:
            self.strategies.remove(strategy)

    def stop_strategies(self):
        # TODO: Need to reset Rego to original state
        self.is_running = False

    def run_strategies(self):
        # TODO: Now as simple as possible
        log.info(f"Strategies started")
        self.is_running = True
        while self.is_running:
            time.sleep(1)
            for strategy in self.strategies:
                if strategy.is_triggerable():
                    log.info(f"Strategy {strategy} triggered")
                    strategy.trigger()
