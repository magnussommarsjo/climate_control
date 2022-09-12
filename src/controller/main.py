import logging
import sys
import traceback
import time

# Setting up logging
FORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="w", format=FORMAT)
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
NETWORK_SLEEP = 60


def main():
    log.info("Main entrypoint started")
    storage = CsvStorage()

    log.info(f"Wait {NETWORK_SLEEP}s for network to connect")
    time.sleep(NETWORK_SLEEP)

    log.info(f"Continious logging started with sample time {SAMPLE_TIME}s")
    continious_logging(storage, sample_time=SAMPLE_TIME)


if __name__ == "__main__":
    main()
