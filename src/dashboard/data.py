from __future__ import annotations

import enum
from typing import Optional, List
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


class Categories(str, enum.Enum):
    TIMESTAMP = "timestamp"
    TEMPERATURE_FIRST_FLOOR = "first_floor.temperature"
    HUMIDITY_FIRST_FLOOR = "first_floor.humidity"
    RADIATOR_FORWARD = "RADIATOR_FORWARD"
    HEAT_CARRIER_RETURN = "HEAT_CARRIER_RETURN"
    HEAT_CARRIER_FORWARD = "HEAT_CARRIER_FORWARD"
    BRINE_IN_EVAPORATOR = "BRINE_IN_EVAPORATOR"
    BRINE_OUT_CONDENSER = "BRINE_OUT_CONDENSER"
    OUTDOOR = "OUTDOOR"
    WARM_WATER_1_TOP = "WARM_WATER_1_TOP"
    HOT_GAS_COMPRESSOR = "HOT_GAS_COMPRESSOR"
    COMPRESSOR = "COMPRESSOR"
    PUMP_COLD_CIRCUIT = "PUMP_COLD_CIRCUIT"
    PUMP_HEAT_CIRCUIT = "PUMP_HEAT_CIRCUIT"
    PUMP_RADIATOR = "PUMP_RADIATOR"
    SWITCH_VALVE_1 = "SWITCH_VALVE_1"
    SWITCH_VALVE_2 = "SWITCH_VALVE_2"
    HEATING_SETPOINT = "HEATING_SETPOINT"
    ROOM_TEMP_SETPOINT = "ROOM_TEMP_SETPOINT"
    EXTRA_WARM_WATER = "EXTRA_WARM_WATER"
    OUTDOOR_TEMP_OFFSET = "OUTDOOR_TEMP_OFFSET"
    SUPP_ENERGY_HEATING = "SUPP_ENERGY_HEATING"
    SUPP_ENERGY_HOTWATER = "SUPP_ENERGY_HOTWATER"
    COMPR_CONS_HEATING = "COMPR_CONS_HEATING"
    COMPR_CONS_HOTWATER = "COMPR_CONS_HOTWATER"
    AUX_CONS_HEATING = "AUX_CONS_HEATING"
    AUX_CONS_HOTWATER = "AUX_CONS_HOTWATER"


COLUMNS = [cat.value for cat in Categories]


class Data:
    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df

    def to_df(self) -> pd.DataFrame:
        return self._df
    
    def filter(self, categories: List[Categories]) -> Data:
        idx = self._df[Schema.CATEGORY].isin(categories)
        return Data(self._df[idx])


    def get_latest_value(self, category: Categories) -> float:
        df = self._df
        return df[df[Schema.CATEGORY] == category][Schema.VALUE].to_list()[-1]


def load_data_from_csv(directory: str, columns: Optional[List[str]] = None) -> Data:
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
    # df[Schema.CATEGORY] = df[Schema.CATEGORY].astype("category") # Category creates issues when filtering
    log.info("Loading data finished")

    return Data(df)

def load_data_from_database() -> Data:
    influx_storage = InfluxStorage(
        address="influxdb2",
        port=8086,
        token=os.getenv("INFLUXDB_TOKEN"),
        org="climate-control",
        bucket="climate-control",
    )

    df = influx_storage.read()
    if df.empty:
        return None
        
    df = df.rename(columns={
        "_time": Schema.TIME,
        "_field": Schema.CATEGORY,
        "_value": Schema.VALUE
    })
    df = df[[Schema.TIME, Schema.CATEGORY, Schema.VALUE]]
    return Data(df)


def main():
    data = load_data_from_csv("")
    df = data.to_df()
    print(df.head())
    print(df.columns)
    print(df.dtypes)

    data.get_latest_value(Categories.TEMPERATURE_FIRST_FLOOR)

    data2 = data.filter([Categories.TEMPERATURE_FIRST_FLOOR, Categories.OUTDOOR])

    print(data2)


if __name__ == "__main__":
    main()
