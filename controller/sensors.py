import logging
import util
import data_central as dc
import time
import datetime
import storage

log = logging.getLogger()


def continious_logging(sample_time: int = 10):
    log.info(f"Continious logging started with sample time {sample_time}s")
    url = "http://192.168.1.21/read/"  # Address to sensor
    csv_storage = storage.CsvStorage(".")

    while True:
        data = dc.get_data_from_url(url)
        if data is None:
            log.info("Could not get reading")
            continue

        # Add time information to data
        timestamp = datetime.datetime.now()
        data['timestamp'] = timestamp.isoformat()
        csv_storage.store(data)

        time.sleep(sample_time)

