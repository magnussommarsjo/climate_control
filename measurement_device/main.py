from utime import sleep
from wifi import WiFi
import machine
import json

from umqtt.simple import MQTTClient

from config import config
import devices
from devices import blink_board


# indicate start of machine
blink_board(1, 2)


MQTT_SERVER = config["mqtt_server"]
DHT_DATA_PIN = config['dht_data_pin']
NETWORK_SSID = config['SSID']
NETWORK_PASSWORD = config['password']
SAMPLE_RATE = config["sample_rate"]
ROOT_TOPIC = config["root_topic"]


def reset():
    """ resets machine """
    machine.reset()
    
def mqtt_connect():
    """Connecte to the MQTT broker"""
    client = MQTTClient(CLIENT_ID, MQTT_SERVER, keepalive=60)
    client.connect()
    print(f"Connected to {MQTT_SERVER} MQTT Broker")
    return client

# Setup devices
board_temperature_sensor = devices.BoardTemperatureSensor()
environment_sensor = devices.ExternalSensor(pin_no=DHT_DATA_PIN)
sensors = [board_temperature_sensor, environment_sensor]

# Connect to network
wifi = WiFi()
try:
    wifi.connect(NETWORK_SSID, NETWORK_PASSWORD)
except RuntimeError as e:
    # Could not connect to wifi
    blink_board(5, 5)  # To indicate reset for user
    reset()

CLIENT_ID = wifi.get_mac()

# Connect to MQTT Broker
try:
    client = mqtt_connect()
except OSError as e:
    print(e)
    print("Failed to connect to the MQTT Broker. Reset machine...")
    reset()

def publish_status(client, msg):
    topic_status = f"{CLIENT_ID}/{ROOT_TOPIC}/status"
    client.publish(topic_status, msg, retain=True)
    print("published", topic_status, msg)

def publish_reading(client, reading):    
    client.publish(f"{CLIENT_ID}/{ROOT_TOPIC}/temperature", str(reading["temperature"]), retain=True)
    client.publish(f"{CLIENT_ID}/{ROOT_TOPIC}/humidity", str(reading["humidity"]), retain=True)
    print(f"published to : {CLIENT_ID}/{ROOT_TOPIC}")

# Publish loop
while True:
    sleep(SAMPLE_RATE)
    reading = environment_sensor.read()
    if reading:
        publish_reading(client, reading)
        publish_status(client, "OK")
    else:
        publish_status(client, "NOT_OK") 
        



# If we end up here the server have failed and we need  to reset the machine
reset()

