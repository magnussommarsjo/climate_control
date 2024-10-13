from typing import Any, NoReturn, Optional
import logging
from .registers import DataType, is_data_type, is_in_data_types
import aiomqtt

log = logging.getLogger(__name__)


class H60:
    def __init__(
        self, client: aiomqtt.Client, id: str | None = None, topic: str = "+/HP/#"
    ):
        """Instantiates an H60 unit

        Args:
            address: IP Address to H60
        """
        self.client = client
        self.topic = topic
        self.id: str | None = id
        self.raw_data: dict = {}

    async def start(self) -> NoReturn:
        await self.client.subscribe(self.topic)
        async for message in self.client.messages:
            self._update_data_from_message(message)

    def _update_data_from_message(self, message: aiomqtt.Message) -> None:
        topic_parts = message.topic.value.split("/")
        if self.id is None:
            self.id = topic_parts[0]

        if len(topic_parts) >= 3:
            key = "/".join(topic_parts[2:])
            value = message.payload.decode("utf-8")

            self.raw_data |= {key: value}

    @staticmethod
    def _convert_raw_value(idx: str, value: str) -> Any:
        """Converts raw value from H60 to its proper data type

        Conversion based on H1 developer manual but modified to work with Rego 1000
        IVT Greenline

        Args:
            idx: Index of the variable
            value: Raw value from H60 request response
        """
        if value is None:
            return None

        if is_in_data_types(
            idx,
            {
                DataType.DEGREES,
                DataType.PERCENT,
                DataType.AMPERE,
            },
        ):
            value = float(value) / 10
        elif is_data_type(idx, DataType.KWH):
            value = float(value) / 100
        elif is_data_type(idx, DataType.ON_OFF_BOOL):
            value = bool(int(value))
        elif is_in_data_types(
            idx,
            {
                DataType.NUMBER,
                DataType.HOURS,
                DataType.MINUTES,
                DataType.DEGREE_MINUTES,
                DataType.KW,
            },
        ):
            value = int(value)
        else:
            raise ValueError(f"Could not identify data type of {idx}")
        return value

    def get_all_data(self, convert: bool = True) -> Optional[dict]:
        data = self.raw_data.copy()
        if convert:
            for idx, value in data.items():
                try:
                    data[idx] = self._convert_raw_value(idx, value)
                except ValueError as e:
                    log.error(e)
        return data

    async def set_variable(self, idx: str, value: str) -> None:
        if self.id is None:
            raise ValueError("Cant identify heatpump id, try set it manually")

        await self.client.publish(f"{self.id}/HP/SET/{idx}", payload=value)
        log.info(f"Tried to set variable {idx} to {value}")

    def get_variable(self, idx: str) -> Any:
        data = self.get_all_data()
        return data[idx]
