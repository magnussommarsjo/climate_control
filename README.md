# Climate Control
This repository supports controlling and monitoring the internal climate of a household utelizing custom climate sensors based on Raspberry pi pico W and a Heatpump Controller from husdata.se

## Installation
Installation of controller packages and monitoring dashboard is done by cloneing this repository, change the current directory into the newly cloned one and running the command
```sh
pip install -e .
```
starting the controller by using command `
```sh
python {path to cloned directory}/climate_control/controller/main.py
```
Starting the dashboard server with
```sh
python {path to cloned directory}/climate_control/dashboard/app.py
```