import logging
from typing import NoReturn
import time
import datetime
from .data_central import get_data_from_url
from .storage import Storage

log = logging.getLogger(__name__)


def continious_logging(storage: Storage, sample_time: int = 10) -> NoReturn:
    url = "http://192.168.1.21/read/"  # Address to sensor

    log.info(f"Continious logging started with sample time {sample_time}s")
    while True:
        data = get_data_from_url(url)
        if data is None:
            continue

        # Add time information to data
        timestamp = datetime.datetime.now()
        data["timestamp"] = timestamp.isoformat()
        storage.store(data)

        time.sleep(sample_time)
