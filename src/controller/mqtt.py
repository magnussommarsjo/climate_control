"""MQTT client


Subscribe to temperature sensors and H60?

"""

from collections import defaultdict
from datetime import datetime
import logging
from queue import Queue
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from controller.config import read_config

log = logging.getLogger(__name__)
config = read_config()

class MQTTHandler:
    def __init__(self, client_id: str, mqtt_host: str, mqtt_port: int) -> None:
        self.client = mqtt.Client(client_id=client_id)
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.message_que: Queue[mqtt.MQTTMessage] = Queue()
        self._callback_registry: dict[str, list[Callable]] = defaultdict(list)

        self._set_up_callback()

    def _set_up_callback(self) -> None:
        """Set up basic callbakc for logging and message que"""

        @self.client.connect_callback()
        def _on_connect(client: mqtt.Client, userdata, flags, rc: mqtt.ReasonCodes) -> None:
            if rc == 0:
                log.info(f"Connected to MQTT Broker {config.MQTT_HOST} on port {config.MQTT_PORT}")
            else:
                log.info(f"Failed_to_connect, return code {rc}")
                
        @self.client.message_callback()
        def _on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
            log.info("\nmessage received " + str(message.payload.decode("utf-8")))
            log.info(f"{message.topic=}")
            log.info(f"{message.qos=}")
            log.info(f"{message.retain=}")
            self._execute_callbacks_from(topic, message)


    def _execute_callbacks_from(self, topic: str, message: str):
        subscriptions = [sub for sub in self._callback_registry.keys() if mqtt.topic_matches_sub(sub, topic)]
        for sub in subscriptions:
            for callback in self._callback_registry[sub]:
                callback(topic, message)
    
    def connect(self):
        self.client.connect(host=self.mqtt_host, port=self.mqtt_port)

    def disconnect(self):
        self.client.disconnect()

    def start(self):
        self.client.loop_start()
    
    def stop(self):
        self.client.loop_stop()

    def register_callback(self, topic: str, callback: Callable[[str, str], None]):
        """Register callback to MQTT topic.
        
        Callback must have two arguments, `topic` and `message` and return `None`.
        >>> def my_callback(some_topic: str, some_message: str) -> None:
        >>>     ...
        >>>
        >>> mqtt_handler.register_callback("some/topic", my_callback)
        """
        self.client.subscribe(topic)
        self._callback_registry[topic].append(callback)
        log.info(f"Callback {callback.__name__} registered to topic {topic}")

    def unregister_callback(self, topic: str, callback: Callable):
        """Unregister the callback function earlier registered"""
        if callback in self._callback_registry[topic]:
            self._callback_registry[topic].remove(callback)
            log.info(f"Callback {callback.__name__} unregistered from topic {topic}")

        if not self._callback_registry[topic]:
            # no one are registered to the topic, unsubscribe
            self.client.unsubscribe(topic)


class MQTTSensor:
    """Sensor to handle callback from subscription. 
    """

    def __init__(self, handler: MQTTHandler,  sub_topic: str) -> None:
        self.sub_topic: str = sub_topic
        handler.register_callback(self.sub_topic, self.update_from_message)

        self.id: str = None
        self.type: str = None
        self.location: str = None
        self.value: float = None
        self.timestamp: Optional[datetime] = None

    def update_from_message(self, topic: str, message: str) -> None:
        """Update sensor with new values"""
        topic_parts = topic.split("/")
        self.id = topic_parts[0],
        self.location = '/'.join(topic_parts[1:-1])
        self.type = topic_parts[-1]
        self.value = float(message)
        self.timestamp = datetime.now()


    def to_dict(self) -> dict:
        return {
            "id": self.value,
            "type": self.type,
            "location": self.location,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"


if __name__ == "__main__":
    # Log to console as well.
    import sys
    import time
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))

    topic = "+/firstfloor/+/humidity"

    def my_callback(*args):
        print("Callback executed")

    def my_other_callback(*args):
        print("This was executed as well")

    handler = MQTTHandler("test_handler", config.MQTT_HOST, config.MQTT_PORT)

    handler.connect()
    handler.register_callback(topic, my_callback)
    handler.register_callback(topic, my_other_callback)
    handler.start()

    time.sleep(10)

    handler.unregister_callback(topic, my_other_callback)
    time.sleep(10)

    handler.stop()
    handler.disconnect()

    print("Main finished")
