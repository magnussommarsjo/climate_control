"""
Main script that starts all threads and processes.
- Creates and starts all the Strategies
- Starts logging of all signals
- Starts the dashboard server
- Initiates logging
- Initiates Controller and type of storage
"""
# Builtin packages
from controller.mqtt import MQTTHandler, MQTTSensor
from controller.config import read_config
from controller.storage import InfluxStorage, CsvStorage, Storage
from controller.sensors import continuous_logging
from controller.strategies import StrategyHandler, OffsetOutdoorTemperatureStrategy
from husdata.controllers import Rego1000
from dashboard import app
from flask import Response
import logging
import sys
import traceback
import threading
from datetime import datetime
from typing import List


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

# External packages

# Local package imports after logging is set up in case of errors when importing packages

config = read_config()


def main():
    log.info("Main entrypoint started")

    mqtt_handler = MQTTHandler(
        client_id=config.MQTT_CLIENT_ID,
        mqtt_host=config.MQTT_HOST,
        mqtt_port=config.MQTT_PORT
    )
    mqtt_handler.connect()

    sensor_firstfloor_temperature = MQTTSensor(
        mqtt_handler, "+/firstfloor/+/temperature")

    mqtt_handler.start()

    rego = Rego1000(config.H60_ADDRESS)

    strategy_threads = set_up_strategies(
        rego=rego, indoor_temp_sensor=sensor_firstfloor_temperature
    )

    # Start all threads. These are 'daemon threads and will be killed as soon as
    # main thread ends. In this case it will be when the dashboard server is closed.
    threads = strategy_threads
    for thread in threads:
        thread.start()

    # Health check.
    # Needs to be defined heer instead of in the app.py module due to checking status
    # of threads.
    @app.app.server.route("/health")
    def health_check():

        # Check threads
        if any(not thread.is_alive() for thread in threads):
            return Response("{'status': 'NOT_OK'}", status=500, mimetype="application/json")

        return Response("{'status': 'OK'}", status=200, mimetype="application/json")

    # Start the dashboard application server
    # NOTE: Debug mode set to 'True' messes upp logging to csv files somehow.
    # Related to threads?
    app.app.run(host=config.HOST, port=config.PORT, debug=False)


def set_up_strategies(
    rego: Rego1000, indoor_temp_sensor: MQTTSensor
) -> List[threading.Thread]:
    """Setting up Control strategies"""
    log.info("Setting up strategies")

    offset_strategy = OffsetOutdoorTemperatureStrategy(
        rego=rego,
        indoor_temperature_callable=lambda: indoor_temp_sensor.value,
        influence=2,
    )
    strategy_handler = StrategyHandler()
    strategy_handler.register_strategy(offset_strategy)

    strategy_thread = threading.Thread(
        name="offset_strategy", target=strategy_handler.run_strategies, daemon=True
    )

    return [strategy_thread]


if __name__ == "__main__":
    main()
