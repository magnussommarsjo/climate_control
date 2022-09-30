from pathlib import Path
import datetime
import csv
import logging
import abc
from typing import Optional, List

from influxdb_client import InfluxDBClient, Point

import controller.util as util

log = logging.getLogger(__name__)

DATA_PATH = Path(__file__).cwd().joinpath("data").resolve()


class Storage(abc.ABC):
    @abc.abstractmethod
    def store(self, data: dict) -> None:
        raise NotImplementedError()


class InfluxStorage(Storage):
    def __init__(self, address: str, port: str, token: str, org: str, bucket: str):
        self.url = f"http://{address}:{port}"
        self.token = token
        self.org = org
        self.bucket = bucket

    def store(self, data: dict) -> None:

        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:

            points = [
                Point("Sensor-data").field(key, value).time(datetime.datetime.utcnow())
                for key, value in util.flatten_dict(data).items()
            ]
            client.write_api().write(self.bucket, points)


class CsvStorage(Storage):
    """Stores data in CSV files by date in defined directory"""

    def __init__(self, folder_path: str = DATA_PATH) -> None:
        path = Path(folder_path)

        if not path.exists():
            path.mkdir()
            log.info(f"Created directory {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path {folder_path} is not a directory")

        self.path = path

        self.fieldnames: Optional[List[str]] = None

    def store(self, data: dict):
        """Stores the data in a CSV format by date"""

        flat_data = util.flatten_dict(data)

        date = datetime.date.today()
        file_name = f"{str(date)}.csv"
        file_path = self.path.joinpath(file_name)

        if not file_path.exists():
            with open(file_path, "w", newline="") as csv_file:
                if self.fieldnames is None:
                    self.fieldnames = list(flat_data.keys())
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerow(flat_data)
        else:
            # First read fieldnames from file if not exist
            if self.fieldnames is None:
                with open(file_path, "r") as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    self.fieldnames = next(csv_reader.reader)
            with open(file_path, "a", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
                writer.writerow(flat_data)
