"""MQTT client


Subscribe to temperature sensors and H60?

"""

import logging
from queue import Queue

import paho.mqtt.client as mqtt

from controller.config import read_config

log = logging.getLogger(__name__)
config = read_config()

message_que: Queue[mqtt.MQTTMessage]  = Queue()
client = mqtt.Client(client_id=config.MQTT_CLIENT_ID)

@client.connect_callback()
def _on_connect(client: mqtt.Client, userdata, flags, rc: mqtt.ReasonCodes) -> None:
    if rc == 0:
        log.info(f"Connected to MQTT Broker {config.MQTT_HOST} on port {config.MQTT_PORT}")
    else:
        log.info(f"Failed_to_connect, return code {rc}")

@client.message_callback()
def _on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage) -> None:
    log.info("\nmessage received " + str(message.payload.decode("utf-8")))
    log.info(f"{message.topic=}")
    log.info(f"{message.qos=}")
    log.info(f"{message.retain=}")

    message_que.put(message)



def connect_client_to_broker(client: mqtt.Client) -> None:
    client.connect(host=config.MQTT_HOST, port=config.MQTT_PORT)


if __name__ == "__main__":
    # Log to console as well.
    import sys
    import time
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))

    connect_client_to_broker(client)
    topic = "+/reading"
    client.subscribe(topic=topic)


    client.loop_start()

    for _ in range(10): # limit to 10 messages
        message = message_que.get(timeout=10)
        print("Got message")

    client.loop_stop()
    client.disconnect()
    print("Main finished")
