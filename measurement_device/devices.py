"""
    Get devices
"""

import machine
from dht import DHT22


board_led = machine.Pin('LED', machine.Pin.OUT)


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
    
    
    