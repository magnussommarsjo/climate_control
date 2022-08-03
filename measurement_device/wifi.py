"""
Connection to WIFI network
"""

import network
import time

class WiFi:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
    
    def connect(self, ssid: str, password: str, max_wait=60):
        self.wlan.connect(ssid, password)
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >=3:
                break
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(1)

        if self.wlan.status() != network.STAT_GOT_IP: # STAT_GOT_IP same as 3
            raise RuntimeError('network connection failed')
        else:
            print('connected')
            status = self.wlan.ifconfig()
            print('ip = ' + status[0])

