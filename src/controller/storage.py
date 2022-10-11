from __future__ import annotations

from pathlib import Path
import datetime
import csv
import logging
import abc
from typing import Optional, List, Tuple

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

import controller.util as util

log = logging.getLogger(__name__)

DATA_PATH = Path(__file__).cwd().joinpath("data").resolve()


class Storage(abc.ABC):
    @abc.abstractmethod
    def store(self, data: dict) -> None:
        raise NotImplementedError()


# from(bucket: "bucket")
#   |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
#   |> filter(fn: (r) => r["_measurement"] == "Test")
#   |> filter(fn: (r) => r["location"] == "home")
#   |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
#   |> yield(name: "mean")
class QueryBuilder:
    """InfluxDB Query builder"""

    def __init__(self) -> None:
        self._query: List[str] = []
        self._has_bucket = False
        self._has_range = False

    def bucket(self, name: str) -> QueryBuilder:
        if self._has_bucket:
            raise DuplicateQueryError("Query already has a call with bucket source")

        self._query.append(f'from(bucket: "{name}")')
        self._has_bucket=True
        return self

    def range(self, start: str, stop: Optional[str] = None) -> QueryBuilder:
        """
        https://docs.influxdata.com/influxdb/cloud/query-data/get-started/query-influxdb/#2-specify-a-time-range
        """
        query = f'range(start: {start}'
        if stop:
            query += f', stop: {stop}'
        query += ')'

        self._query.append(query)
        self._has_range = True
        return self
    
    def filter(self, key: str, value: str) -> QueryBuilder:
        self._query.append(f'filter(fn: (r) => r["{key}"] == "{value}")')
        return self
    
    def measurement(self, name: str) -> QueryBuilder:
        return self.filter("_measurement", name)


    def build(self, validate=True) -> str:
        if  validate:
            if not self._has_bucket:
                raise MissingQueryError("Missing bucket")

            if not self._has_range:
                raise MissingQueryError("Missing range in query")
        
        self._query.append('yield()')

        return "\n  |> ".join(self._query)
    
    def __str__(self) -> str:
        return self.build(validate=False)

class MissingQueryError(Exception):
    pass

class DuplicateQueryError(Exception):
    pass

class InfluxStorage(Storage):
    def __init__(self, address: str, port: str, token: str, org: str, bucket: str):
        self.url = f"http://{address}:{port}"
        self.token = token
        self.org = org
        self.bucket = bucket

    def store(
        self, data: dict, measurement: str = "default",  tags: Optional[List[Tuple[str, str]]] = None
    ) -> None:

        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            time = datetime.datetime.utcnow()
            points = [
                Point(measurement).field(key, value).time(time)
                for key, value in util.flatten_dict(data).items()
            ]

            for point in points:
                for tag in tags:
                    point.tag(tag[0], tag[1])

            with client.write_api(write_options=SYNCHRONOUS) as write_api:
                write_api.write(bucket=self.bucket, record=points)
    
    def read(self, query: Optional[str] = None) -> pd.DataFrame:
        """Query the influx database and return a dataframe. 
        If no query is specified then return everything from the bucket the past 24h
        """
        if query is None:
            # Load everything past 24h
            query = QueryBuilder().bucket(self.bucket).range("-24h").build()

        with InfluxDBClient(url=self.url, token=self.token, org=self.org) as client:
            response = client.query_api().query_data_frame(query)
        
        if isinstance(response, list):
            response = pd.concat(response)

        return response


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
