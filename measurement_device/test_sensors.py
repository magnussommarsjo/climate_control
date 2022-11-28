"""Test sensors and leds

Leds should be blinking while measurements is read.
"""
import utime
from devices import ExternalSensor, BoardTemperatureSensor, board_led
from machine import Pin
     
e_sensor = ExternalSensor(2)
b_sensor = BoardTemperatureSensor()

while True:    
    utime.sleep(2)
    print(f"{'New reading':_^80}")
    board_led.on()
    print(f"\n{'External Sensor':_<60}")
    reading = e_sensor.read()
    print(reading)
    
    
    print(f"\n{'Board Sensor':_<60}")
    reading = b_sensor.read()
    print(reading)
    board_led.off()
