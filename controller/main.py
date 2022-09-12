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
from sensors import continious_logging
from storage import CsvStorage

def main():
    log.info("Main entrypoint started")
    time.sleep(60) # Give time for Network to connect
    storage = CsvStorage()
    continious_logging(storage, sample_time=10)


if __name__ == "__main__":
    main()
