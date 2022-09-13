import pandas as pd
from pathlib import Path
import logging

log = logging.getLogger(__name__)

class Schema:
    TIME = "timestamp"
    CATEGORY = "variable"
    VALUE = "value"


def load_data(directory: str) -> pd.DataFrame:
    path = Path(directory)
    log.info(f"Loading of data at directory {path}")
    if not path.exists:
        raise FileNotFoundError("Directory or file does not exixst")

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
    df[Schema.CATEGORY] = df[Schema.CATEGORY].astype("category")
    log.info("Loading data finished")

    return df


def main():
    df = load_data("")
    print(df.head())
    print(df.columns)
    print(df.dtypes)


if __name__ == "__main__":
    main()
