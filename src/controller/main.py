"""
Main script that starts all threads and processes.
- Creates and starts all the Strategies
- Starts logging of all signals
- Starts the dashboard server
- Initiates logging
- Initiates Controller and type of storage
"""

import logging
import os
import sys
import traceback
import threading
import time
from datetime import datetime
from typing import List
from flask import Response, make_response


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
log.addHandler(consoleHandler)

# Logg all unhandled exceptions
def exception_handler(*exc_info):
    msg = "".join(traceback.format_exception(*exc_info))
    log.exception(f"Unhandled exception: {msg}")


sys.excepthook = exception_handler

# Local package imports after logging is set up in case of errors when importing packages
from dashboard import app
from husdata.controllers import Rego1000
from controller.strategies import StrategyHandler, OffsetOutdoorTemperatureStrategy
from controller.sensors import continuous_logging, Sensor
from controller.storage import InfluxStorage, CsvStorage, Storage
from controller.config import read_config

config = read_config() 

def main():
    log.info("Main entrypoint started")

    storage = set_up_storage()

    first_floor_sensor = Sensor(name="first_floor", address="192.168.1.21")
    rego = Rego1000(config.H60_ADDRESS)

    strategy_threads = set_up_strategies(
        rego=rego, indoor_temp_sensor=first_floor_sensor
    )
    logging_thread = set_up_logging(
        rego=rego, indoor_temp_sensor=first_floor_sensor, storage=storage
    )

    # Start all threads. These are 'daemon threads and will be killed as soon as
    # main thread ends. In this case it will be when the dashboard server is closed.
    threads = [logging_thread, *strategy_threads]
    _ = [thread.start() for thread in threads]

    # Health check.
    # Needs to be defined heer instead of in the app.py module due to checking status
    # of threads.
    @app.app.server.route("/health")
    def health_check():

        # Check threads
        if any(not thread.is_alive() for thread in threads):
            return Response("{status: not_ok}", status=500, mimetype="application/json")

        return Response("{status: ok}", status=200, mimetype="application/json")

    # Start the dashboard application server
    # NOTE: Debug mode set to 'True' messes upp logging to csv files somehow.
    # Related to threads?
    app.app.run(host=config.HOST, port=config.PORT, debug=False)


def set_up_storage() -> Storage:
    """Set up storage.

    If we have a token for InfluxDB the assume that is the storage to use.
    Otherwise we fallback on a simple CsvStorage.
    """

    if config.INFLUXDB_TOKEN:
        storage = InfluxStorage(
            address=config.INFLUXDB_ADDRESS,
            port=config.INFLUXDB_PORT,
            token=config.INFLUXDB_TOKEN,
            org="climate-control",
            bucket="climate-control",
        )
    else:
        storage = CsvStorage()

    log.info(f"Storage {storage} instantiated.")
    return storage


def set_up_logging(
    indoor_temp_sensor: Sensor, rego: Rego1000, storage: Storage
) -> threading.Thread:
    """Set up logging.

    Setting up continuous logging signals both from custom sensors as well as
    the Rego1000 controller via H60Gateway
    """

    def get_data_from_sensors() -> dict:
        """Function to be used in continuous logging"""
        if indoor_temp_sensor.update():
            sensor_data = indoor_temp_sensor.to_dict()
        else:
            sensor_data = {}

        rego_data = rego.get_all_data()
        if rego_data is not None:
            rego_data = Rego1000.translate_data(rego_data)
        else:
            rego_data = {}
        timestamp = datetime.now().isoformat()
        return {"timestamp": timestamp, **sensor_data, **rego_data}

    logging_thread = threading.Thread(
        name="logging",
        target=continuous_logging,
        args=(get_data_from_sensors, storage, config.SAMPLE_TIME),
        daemon=True,
    )

    return logging_thread


def set_up_strategies(
    rego: Rego1000, indoor_temp_sensor: Sensor
) -> List[threading.Thread]:
    """Setting up Control strategies"""
    offset_strategy = OffsetOutdoorTemperatureStrategy(
        rego=rego,
        indoor_temperature_callable=lambda: indoor_temp_sensor.temperature,
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
