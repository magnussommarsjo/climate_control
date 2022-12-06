"""
Main script that starts all threads and processes.
- Creates and starts all the Strategies
- Starts logging of all signals
- Starts the dashboard server
- Initiates logging
- Initiates Controller and type of storage
"""
# Builtin packages
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
from flask import Response

# Local package imports after logging is set up in case of errors when importing packages
from dashboard import app
from husdata.controllers import Rego1000
from controller.strategies import StrategyHandler, OffsetOutdoorTemperatureStrategy
from controller.sensors import continuous_logging, MQTTSensor
from controller.storage import InfluxStorage, CsvStorage, Storage
from controller.config import read_config
from controller.mqtt import MQTTHandler

config = read_config()


def main():
    log.info("Main entrypoint started")

    mqtt_handler = MQTTHandler(
        client_id=config.MQTT_CLIENT_ID, 
        mqtt_host=config.MQTT_HOST, 
        mqtt_port=config.MQTT_PORT
        )
    mqtt_handler.connect()

    storage = set_up_storage()

    first_floor_sensor = MQTTSensor(name="first_floor")
    mqtt_handler.register_callback("+/sensor/reading", first_floor_sensor.update)

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
    
    log.info("Setting up storage")

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
    indoor_temp_sensor: MQTTSensor, rego: Rego1000, storage: Storage
) -> threading.Thread:
    """Set up logging.

    Setting up continuous logging signals both from custom sensors as well as
    the Rego1000 controller via H60Gateway
    """
    
    log.info("Setting up logging")

    def get_data_from_sensors() -> dict:
        """Function to be used in continuous logging"""
        
        sensor_data = indoor_temp_sensor.to_dict()

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
    rego: Rego1000, indoor_temp_sensor: MQTTSensor
) -> List[threading.Thread]:
    """Setting up Control strategies"""
    log.info("Setting up strategies")

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
