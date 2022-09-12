from pathlib import Path
import datetime
import util
import csv
import logging
import abc

log = logging.getLogger(__name__)

DATA_PATH = Path(__file__).parent.joinpath("data").resolve()


class Storage(abc.ABC):
    @abc.abstractmethod
    def store(self, data: dict) -> None:
        raise NotImplementedError()


class CsvStorage(Storage):
    def __init__(self, folder_path: str = DATA_PATH) -> None:
        path = Path(folder_path)

        if not path.exists():
            path.mkdir()
            log.info(f"Created directory {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path {folder_path} is not a directory")

        self.path = path

    def store(self, data: dict):
        """Stores the data in a CSV format by date"""

        flat_data = util.flatten_dict(data)

        date = datetime.date.today()
        file_name = f"{str(date)}.csv"
        file_path = self.path.joinpath(file_name)

        if not file_path.exists():
            with open(file_path, "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=flat_data.keys())
                writer.writeheader()
                writer.writerow(flat_data)
        else:
            with open(file_path, "a", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=flat_data.keys())
                writer.writerow(flat_data)
