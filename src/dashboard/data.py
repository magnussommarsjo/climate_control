import pandas as pd
from pathlib import Path
import logging
import os
from controller.storage import (
    InfluxStorage,
    QueryBuilder,
)  # Todo: Coupling that is unwanted

log = logging.getLogger(__name__)

class Schema:
    TIME = "timestamp"
    CATEGORY = "variable"
    VALUE = "value"


def load_data_from_csv(directory: str) -> pd.DataFrame:
    path = Path(directory)
    log.info(f"Loading of data at directory {path}")
    if not path.exists:
        raise FileNotFoundError("Directory or file does not exist")

    # Load data from all csv files
    all_files = list(path.glob("*.csv"))
    log.info(f"Found {len(all_files)} files to read")
    all_files.sort()
    data_files = [pd.read_csv(filename) for filename in all_files[-2:]]

    # Concatenate data and transform to long format
    df = pd.concat(data_files, axis=0, ignore_index=True)
    df = df.melt(id_vars=Schema.TIME)

    # Convert datatypes
    df[Schema.TIME] = pd.to_datetime(df[Schema.TIME])
    log.info("Loading data finished")

    return df

def load_data_from_database() -> pd.DataFrame:
    influx_storeage = InfluxStorage(
        adderss="localhost",
        port=8086,
        token=os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"),
        org="climate-control",
        bucket=os.getenv("DOCKER_INFLUXDB_INIT_BUCKET", "climate-control"),
    )

    df = influx_storeage.read()
    df = df.rename(columns={
        "_time": Schema.TIME,
        "_field": Schema.CATEGORY,
        "_value": Schema.VALUE
    })
    df = df[[Schema.TIME, Schema.CATEGORY, Schema.VALUE]]
    return df



def main():
    df = load_data_from_csv("")
    print(df.head())
    print(df.columns)
    print(df.dtypes)


if __name__ == "__main__":
    main()
