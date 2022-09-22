import logging
import sys
import time
import traceback
import threading


# Setting up logging
FORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
logging.basicConfig(
    level=logging.INFO, filename="log_controller.txt", filemode="w", format=FORMAT
)
log = logging.getLogger(__name__)

# Logg all unhandled exceptions
def exception_handler(*exc_info):
    msg = "".join(traceback.format_exception(*exc_info))
    log.exception(f"Unhandeled exception: {msg}")


sys.excepthook = exception_handler

# Local package imports after logging is set up in case of errors when importing packages
from dashboard import app
from husdata.controllers import Rego1000
from controller.strategies import StrategyHandler, OffsetOutdoorTemperatureStrategy
from controller.sensors import continious_logging, Sensor
from controller.storage import CsvStorage

SAMPLE_TIME = 10
H60_IP_ADDRESS = "192.168.1.12"


def main():
    log.info("Main entrypoint started")
    storage = CsvStorage()
    first_floor_sensor = Sensor(name="first_floor", address="192.168.1.21")

    logging_thread = threading.Thread(
        target=continious_logging,
        args=(first_floor_sensor, storage, SAMPLE_TIME),
        daemon=True,
    )
    logging_thread.start()

    # Setting up Control strategies
    rego = Rego1000(H60_IP_ADDRESS)
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
    strategy_thread.start()

    app.app.run(port=app.PORT, debug=False)
    # NOTE: Debug mode set to 'True' messes upp logging to csv files somehow.
    # Related to threads?


if __name__ == "__main__":
    main()
