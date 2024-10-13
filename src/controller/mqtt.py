"""MQTT client


Subscribe to temperature sensors and H60?

"""

from datetime import datetime
import logging
from typing import Optional, NoReturn

import aiomqtt

log = logging.getLogger(__name__)


class MQTTSensor:
    """Sensor to handle callback from subscription. 
    """

    def __init__(self, client: aiomqtt.Client, sub_topic: str, name: str) -> None:
        self.client = client
        self.sub_topic: str = sub_topic
        self.name = name
        self.id: str = None
        self.value: float = None
        self.timestamp: Optional[datetime] = None

    def update_from_message(self, message: aiomqtt.Message) -> None:
        """Update sensor with new values"""
        topic = message.topic.value
        topic_parts = topic.split("/")
        self.id = topic_parts[0],
        self.value = float(message.payload)
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        return dict(
            name=self.name,
            id=self.id,
            value=self.value,
            timestamp=self.timestamp.isoformat() if self.timestamp is not None else None
        )


    async def start_sensor(self) -> NoReturn:
        await self.client.subscribe(self.sub_topic)
        async for message in self.client.messages:
            self.update_from_message(message)


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

