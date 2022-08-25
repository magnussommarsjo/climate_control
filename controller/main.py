import logging
import sys
import traceback

# Setting up logging
FORMAT = "%(asctime)s::%(levelname)s::%(name)s::%(message)s"
logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="w", format=FORMAT)
log = logging.getLogger(__name__)

# Logg all unhandled exceptions
def exception_handler(*exc_info):
    msg = "".join(traceback.format_exception(*exc_info))
    log.exception(f"Unhandeled exception: {msg}")


sys.excepthook = exception_handler


def main():
    from sensors import continious_logging

    continious_logging(sample_time=5)


if __name__ == "__main__":
    main()
