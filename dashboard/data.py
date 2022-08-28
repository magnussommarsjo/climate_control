import pandas as pd
from pathlib import Path
import enum


class Schema(str, enum.Enum):
    TIME = "timestamp"
    HUMIDITY = "external_temperature_sensor.humidity"
    TEMPERATURE = "external_temperature_sensor.temperature"
    BOARD_VOLTGE = "board_temperature_sensor.voltage"
    BOARD_TEMPERATURE = "board_temperature_sensor.temperature"


def load_data(directory: str) -> pd.DataFrame:
    path = Path(directory)
    if not path.exists:
        raise FileNotFoundError("Directory or file does not exixst")

    all_files = path.glob("*.csv")
    data_files = [pd.read_csv(filename) for filename in all_files]

    df = pd.concat(data_files, axis=0, ignore_index=True)
    df[Schema.TIME] = pd.to_datetime(df[Schema.TIME])

    return df


def main():
    df = load_data("")
    print(df.head())


if __name__ == "__main__":
    main()
