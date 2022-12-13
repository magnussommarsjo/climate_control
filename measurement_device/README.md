# Pico W sensor and webserver

## Assembly
The wiring is quite simple. We only need the DHT22 sensor and the data pin connecting to pin 4 (GP2) 
![Pico W Wiring](../attachments/pico_sensor_wiring.jpg)
## Installation

Follow the instructions on the [micropython website](https://micropython.org/download/rp2-pico-w/) to flash the raspberry pi pico W with the latest firmware. 

Using [thonny IDE](https://thonny.org/) you can copy the python files to the board. Files to be copied is:  
- config.py
- devices.py
- wifi.py
- main.py

The `test_sensors.py` file is only needed for debugging to make sure that everything is set upp correct. 

`requirements.txt` is needed to install required packages to the pico via thonny. 

Also a file `config.json` needs to be created on the board including the following information: 
```json
{
    "SSID": "YOUR_WIFI_SSID",
    "password": "YOUR_WIFI_PASSWORD",
    "sample_rate": 10,  # time in seconds between mqtt publish
    "dht_data_pin": 2,  # Pin where data is connected
    "mqtt_server": "SERVER_ADDRESS",
    "mqtt_port": 1883,
    "root_topic": "floor/room",
}
```

Then when booted the sensor will start sending messages to the MQTT broker with topic according to `{device_mac_address}/{root_topic}/{type}` where `type` is ether temperature or humidity and the message is a string with the measurement value.
