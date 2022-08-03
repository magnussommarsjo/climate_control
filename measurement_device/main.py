import json

from config import config
from wifi import WiFi
from webserver import Webserver
import devices


# Setup devices
led = devices.board_led
board_temperature_sensor = devices.BoardTemperatureSensor()
environment_sensor = devices.ExternalSensor(pin_no=2)  # TODO: Read from configuration file later

sensors = [board_temperature_sensor, environment_sensor]

# Connect to network
wifi = WiFi()
wifi.connect(config['SSID'], config['password'])


# Start Webserver
webserver = Webserver(sensors)
webserver.start()
