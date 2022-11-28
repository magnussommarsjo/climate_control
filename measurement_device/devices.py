"""
    Get devices
"""

import machine
from utime import sleep
from dht import DHT22


board_led = machine.Pin('LED', machine.Pin.OUT)

def blink_board(duration: int, frequency: float):
    """Blinks led light for a period of time"""
    if frequency < 0 or duration < 0:
        raise ValueError("arguments cant be 0 or below")
    
    delay = 1 / frequency / 2
    num_cycles = int(duration * frequency)
    
    board_led.off()
    for _ in range(num_cycles):
        board_led.on()
        sleep(delay)
        board_led.off()
        sleep(delay)
        


class Sensor:
    """
    Base Class for all Sensors
    
    Defines interfaces that must be implemented.
    
    Attributes:
        id: the name of the device
    """
    id: str
    
    def read():
        """
        Reads measurements from the sensor

        Returns:
            Measurement values as a dictionary
        """
        raise NotImplementedError()
        


class BoardTemperatureSensor(Sensor):
    def __init__(self, pin=4, constants=(27, 0.706, 0.001721), id = "board_temperature_sensor"):
        self.id = id
        self.a, self.b, self.c = constants
        self.conv_fact = 3.3/65535
        self.sensor = machine.ADC(pin)
    
    def _read_volt(self):
        return self.sensor.read_u16() * self.conv_fact
    
    def read(self):
        voltage = self._read_volt()
        temperature = self.a - (voltage - self.b)/self.c
        return {"temperature": temperature, "voltage": voltage}
    
    
class ExternalSensor(Sensor):
    """External temperature sensor based on DHT22"""
    
    def __init__(self, pin_no, id="external_temperature_sensor"):
        self.id = id
        self.sensor = DHT22(machine.Pin(pin_no, machine.Pin.PULL_UP))
    
    def read(self):
        """Reads temperature and humidity as a dictionary.

        If unsucessfull return None.
        """
        try:
            self.sensor.measure()
            temperature = self.sensor.temperature()
            humidity = self.sensor.humidity()
            
            return {"temperature": temperature, "humidity": humidity}
        except OSError as e:
            print(e)
            return None
    
    
    