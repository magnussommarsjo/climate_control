import pandas as pd
from pathlib import Path
import logging

log = logging.getLogger(__name__)


class Schema:
    TIME = "timestamp"
    CATEGORY = "variable"
    VALUE = "value"


COLUMNS = [
    "timestamp",
    "first_floor.temperature",
    "first_floor.humidity",
    "RADIATOR_FORWARD",
    "HEAT_CARRIER_RETURN",
    "HEAT_CARRIER_FORWARD",
    "BRINE_IN_EVAPORATOR",
    "BRINE_OUT_CONDENSER",
    "OUTDOOR",
    "WARM_WATER_1_TOP",
    "HOT_GAS_COMPRESSOR",
    "COMPRESSOR",
    "PUMP_COLD_CIRCUIT",
    "PUMP_HEAT_CIRCUIT",
    "PUMP_RADIATOR",
    "SWITCH_VALVE_1",
    "SWITCH_VALVE_2",
    "HEATING_SETPOINT",
    "ROOM_TEMP_SETPOINT",
    "EXTRA_WARM_WATER",
    "OUTDOOR_TEMP_OFFSET",
    "SUPP_ENERGY_HEATING",
    "SUPP_ENERGY_HOTWATER",
    "COMPR_CONS_HEATING",
    "COMPR_CONS_HOTWATER",
    "AUX_CONS_HEATING",
    "AUX_CONS_HOTWATER",
]


def load_data(directory: str) -> pd.DataFrame:
    path = Path(directory)
    log.info(f"Loading of data at directory {path}")
    if not path.exists:
        raise FileNotFoundError("Directory or file does not exist")

    # Load data from all csv files
    all_files = list(path.glob("*.csv"))
    log.info(f"Found {len(all_files)} files to read")
    all_files.sort()
    data_files = [pd.read_csv(filename) for filename in all_files[-2:]]

    if not data_files:
        return None

    # Concatenate data and transform to long format
    df = pd.concat(data_files, axis=0, ignore_index=True)
    df = df[COLUMNS]
    df = df.melt(id_vars=Schema.TIME)

    # Convert datatypes
    df[Schema.TIME] = pd.to_datetime(df[Schema.TIME])
    df[Schema.CATEGORY] = df[Schema.CATEGORY].astype("category")
    log.info("Loading data finished")

    return df


def main():
    from controller.storage import DATA_PATH

    df = load_data(DATA_PATH)
    print(df.head())
    print(df.columns)
    print(df.dtypes)


if __name__ == "__main__":
    main()
