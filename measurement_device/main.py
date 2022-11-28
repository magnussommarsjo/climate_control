from config import config
from wifi import WiFi
from webserver import Webserver
import devices
from devices import blink_board
import machine

# indicate start of machine
blink_board(1, 2)

def reset():
    """ resets machine """
    machine.reset()

# Setup devices
board_temperature_sensor = devices.BoardTemperatureSensor()
environment_sensor = devices.ExternalSensor(pin_no=config['dht_data_pin'])
sensors = [board_temperature_sensor, environment_sensor]

# Connect to network
wifi = WiFi()
try:
    wifi.connect(config['SSID'], config['password'])
except RuntimeError as e:
    # Could not connect to wifi
    blink_board(5, 5)  # To indicate reset for user
    reset()


# Start Webserver
webserver = Webserver(sensors)
webserver.start()

# If we end up here the server have failed and we need  to reset the machine
reset()

