import logging
import sys
import traceback
import time
import threading

from dashboard import app
from husdata.controllers import Rego1000
from controller.strategies import StrategyHandler, OffsetOutdoorTemperatureStrategy

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
from controller.sensors import continious_logging
from controller.storage import CsvStorage

SAMPLE_TIME = 60
H60_IP_ADDRESS = "192.168.1.12"


def main():
    log.info("Main entrypoint started")
    storage = CsvStorage()

    logging_thread = threading.Thread(
        target=continious_logging, args=(storage, SAMPLE_TIME), daemon=True
    )
    logging_thread.start()

    # Setting up Control strategies
    rego = Rego1000(H60_IP_ADDRESS)
    
    def get_temperature_function() -> float:
        log.debug(f"Temporary function returning ac onstant")
        return 24.5

    offset_strategy = OffsetOutdoorTemperatureStrategy(
        rego, get_temperature_function, 2
    )
    strategy_handler = StrategyHandler()
    strategy_handler.register_strategy(offset_strategy)

    strategy_thread = threading.Thread(
        target=strategy_handler.run_strategies, daemon=True
    )
    strategy_thread.start()

    app.app.run(port=app.PORT, debug=True)


if __name__ == "__main__":
    main()
