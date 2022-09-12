import pandas as pd
from pathlib import Path


class Schema:
    TIME = "timestamp"
    CATEGORY = "variable"
    VALUE = "value"


def load_data(directory: str) -> pd.DataFrame:
    path = Path(directory)
    if not path.exists:
        raise FileNotFoundError("Directory or file does not exixst")

    # Load data from all csv files
    all_files = path.glob("*.csv")
    data_files = [pd.read_csv(filename) for filename in all_files]

    # Concatenate data and transform to long format
    df = pd.concat(data_files, axis=0, ignore_index=True)
    df = df.melt(id_vars=Schema.TIME)

    # Convert datatypes
    df[Schema.TIME] = pd.to_datetime(df[Schema.TIME])
    df[Schema.CATEGORY] = df[Schema.CATEGORY].astype("category")

    return df


def main():
    df = load_data("")
    print(df.head())
    print(df.columns)
    print(df.dtypes)


if __name__ == "__main__":
    main()
