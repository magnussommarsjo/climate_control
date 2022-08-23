import util
import data_central as dc
import time
import datetime
import storage
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

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

    log.info(util.print_dict(data))
    time.sleep(10)
        
