"""
Webserver
"""

import socket
import json

class Webserver:
    def __init__(self, sensors):
        """
            sensors: A list of sensors
        """
        self.sensors = sensors
    
    def start(self):
        
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        try:
            s.bind(addr)
            s.listen(1)
            print('listening on', addr)

            # Listen for connections
            while True:
                self._handle_connection(s)
            
        # Close the socket connection if any error occurs.
        finally:
            print('Socket closed')
            s.close()
            
    def _handle_connection(self, s):
        """
        s: Socket
        """
        try:
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)
            
            request = str(request)
            
            read_request = request.find('/read/')
            print('read request = ' + str(read_request))
            
            data = {}
            if read_request == 6:
                print("Reading from sensors")
                for sensor in self.sensors:
                    data[sensor.id] = sensor.read()
                
            response = json.dumps(data)
            
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()
        
        except OSError as e:
            cl.close()
            print('connection closed')
