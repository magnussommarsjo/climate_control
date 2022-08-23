from pathlib import Path
import datetime
import util
import csv

class CsvStorage:
    def __init__(self, folder_path: str) -> None:
        path = Path(folder_path)

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
            with open(file_path, 'w', newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames = flat_data.keys())
                writer.writeheader()
                writer.writerow(flat_data)
        else:
            with open(file_path, 'a', newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames = flat_data.keys())
                writer.writerow(flat_data)


