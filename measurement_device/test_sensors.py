import utime

from sensors import TemperatureSensor

from machine import Pin
from dht import DHT22
     


sensor = TemperatureSensor()

dht_data_pin = Pin(2, Pin.IN, Pin.PULL_UP)
dht_sensor = DHT22(dht_data_pin)

while True:
    
    utime.sleep(2)
    reading = sensor.read()
    volt = sensor.read_volt()
    print("Board Sensor:")
    print(f"Temperature {reading:.1f}°C")
    print(f"Volt {volt:.2f}V")
    print("")
    
    dht_sensor.measure()
    T_dht = dht_sensor.temperature()
    H_dht = dht_sensor.humidity()
    
    print("DHT Sensor:")
    if T_dht:
        print(f"Temperature {T_dht:.1f}°C")
    else:
        print("Temperature error")
        
    if H_dht:
        print(f"Humidity {H_dht:.1f}V")
    else:
        print("Humidity error")
    print("")
    
