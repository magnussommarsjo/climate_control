"""
Main script that starts all threads and processes.
- Creates and starts all the Strategies
- Starts logging of all signals
- Starts the dashboard server
- Initiates logging
- Initiates Controller and type of storage
"""

# Builtin packages
import asyncio
from typing import NoReturn

import aiomqtt
from controller.mqtt import MQTTSensor
from controller.config import read_config
from controller.strategies import StrategyHandler, OffsetOutdoorTemperatureStrategy
from husdata.controllers import Rego1000
import logging
import sys
import traceback


# Setting up logging
FORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
logging.basicConfig(
    level=logging.INFO, filename="log_controller.txt", filemode="w", format=FORMAT
)
log = logging.getLogger(__name__)


# Log to console as well.
consoleHandler = logging.StreamHandler()
logFormatter = logging.Formatter(FORMAT)
consoleHandler.setFormatter(logFormatter)

# Add consolHandler to all loggers
for name, item in logging.root.manager.loggerDict.items():
    if isinstance(item, logging.Logger):
        item.addHandler(consoleHandler)

# Logg all unhandled exceptions


def exception_handler(*exc_info):
    msg = "".join(traceback.format_exception(*exc_info))
    log.exception(f"Unhandled exception: {msg}")


sys.excepthook = exception_handler

config = read_config()


async def log_sensors(sensors: list[MQTTSensor]) -> NoReturn:
    while True:
        for sensor in sensors:
            log.info(f"{sensor.to_dict()}")
        await asyncio.sleep(2)


async def main():
    client = aiomqtt.Client(config.MQTT_HOST, username="climate-control")

    temperature_sensor = MQTTSensor(
        client, "+/firstfloor/+/temperature", name="temperature"
    )
    humidity_sensor = MQTTSensor(client, "+/firstfloor/+/humidity", name="humidity")

    async with client:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(temperature_sensor.start_sensor())
            tg.create_task(humidity_sensor.start_sensor())
            tg.create_task(log_sensors([temperature_sensor, humidity_sensor]))

    # rego = Rego1000(config.H60_ADDRESS)

    # strategy_threads = set_up_strategies(
    #     rego=rego, indoor_temp_sensor=sensor_firstfloor_temperature
    # )


if __name__ == "__main__":
    log.info("Main entrypoint started")
    asyncio.run(main())
    log.info("stoped")
