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

import aiomqtt
from controller.mqtt import MQTTSensor
from controller.config import read_config
from controller.strategies import OffsetOutdoorTemperatureStrategy
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

async def main():
    client = aiomqtt.Client(config.MQTT_HOST, username="climate-control")

    temperature_sensor = MQTTSensor(
        client,
        "+/firstfloor/+/temperature",
        name="temperature",
    )
    rego = Rego1000(client, id="8cce4efb8623", topic="8cce4efb8623/HP/#")

    strategy = OffsetOutdoorTemperatureStrategy(
        rego=rego,
        temperature_sensor=temperature_sensor,
        influence=config.STRATEGY_INFLUENCE,
        period=config.STRATEGY_PERIOD,
    )

    async with client:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(temperature_sensor.start_sensor())
            tg.create_task(rego.start())
            tg.create_task(strategy.start())


if __name__ == "__main__":
    log.info("Main entrypoint started")
    asyncio.run(main())
    log.info("stoped")
