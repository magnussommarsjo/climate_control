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
from datetime import datetime


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
from controller.storage import InfluxStorage

SAMPLE_TIME = 60
H60_IP_ADDRESS = "192.168.1.12"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 80)


def main():
    log.info("Main entrypoint started")

    # Global objects used by multiple threads
    storage = InfluxStorage(
        address='influxdb2',
        port=8086,
        token=os.getenv("INFLUXDB_TOKEN"),
        org="climate-control",
        bucket="climate-control",

    )
    first_floor_sensor = Sensor(name="first_floor", address="192.168.1.21")
    rego = Rego1000(H60_IP_ADDRESS)

    # Setting up continuous logging signals both from custom sensors as well as
    # the Rego1000 controller via H60Gateway
    def get_data_from_sensors() -> dict:
        """Function to be used in continuous logging"""
        first_floor_sensor.update()
        sensor_data = first_floor_sensor.to_dict()
        rego_data = rego.get_all_data()
        rego_data = Rego1000.translate_data(rego_data)
        timestamp = datetime.now().isoformat()
        return {"timestamp": timestamp, **sensor_data, **rego_data}

    logging_thread = threading.Thread(
        target=continuous_logging,
        args=(get_data_from_sensors, storage, SAMPLE_TIME),
        daemon=True,
    )

    # Setting up Control strategies
    offset_strategy = OffsetOutdoorTemperatureStrategy(
        rego=rego,
        indoor_temperature_callable=lambda: first_floor_sensor.temperature,
        influence=2,
    )
    strategy_handler = StrategyHandler()
    strategy_handler.register_strategy(offset_strategy)

    strategy_thread = threading.Thread(
        target=strategy_handler.run_strategies, daemon=True
    )

    # Start all threads. These are 'daemon threads and will be killed as soon as
    # main thread ends. In this case it will be when the dashboard server is closed.
    threads = [
        logging_thread, 
        strategy_thread
    ]
    _ = [thread.start() for thread in threads]

    # Start the dashboard application server
    app.app.run(host=HOST, port=PORT, debug=False)
    # NOTE: Debug mode set to 'True' messes upp logging to csv files somehow.
    # Related to threads?


if __name__ == "__main__":
    main()
