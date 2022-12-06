# Implementation plan of mqtt


```mermaid
flowchart LR
    sensor[Sensor]
    subgraph SERVER
    controller[Controller]
    influxdb[(InfluxDB)]
    end
    h60[Husdata H60]

    sensor <-- REST --> controller
    controller ~~~~ h60
    controller --> influxdb
    controller <-- REST --> h60

```

## Overview
Dashed lines are not implemented but are potential way of doing comunicattion. 

```mermaid
flowchart LR
    sensor[Sensor]
    subgraph SERVER
    mqtt_broker[MQTT Broker]
    controller[Controller]
    influxdb[(InfluxDB)]
    end
    h60[Husdata H60]


    sensor -- id/sensor/reading --> mqtt_broker
    controller ~~~~ h60
    mqtt_broker -- +/sensor/reading ---> controller
    mqtt_broker -.-> influxdb
    controller --> influxdb
    controller <-- REST --> h60
    h60 -.-> mqtt_broker

```

## Controller (present)
Issues with present solution

- Double storage connections due to two diffrent packages. But this could be assigned through function arguments?

```mermaid
flowchart TD
    sensors[Sensor connection]
    h60[H60 Connection]
    logging([logging thread])
    strategies([strategies thread])
    dashboard([Dashboard thread])

    subgraph Storage
    storeage[Storage connection main]
    storeage2[Storage connection dash]
    end

    sensors --> logging
    sensors --> strategies
    logging --> storeage
    strategies --> h60
    h60 --> strategies
    h60 --> logging
    storeage2 --> dashboard

```


## First step
Remove direct connection with Sensors

```mermaid
flowchart TD
    sensors[/sensor publish\]
    h60[H60 Connection]
    logging([logging thread])
    strategies([strategies thread])
    dashboard([Dashboard thread])

    subgraph Storage
    storeage[Storage connection main]
    storeage2[Storage connection dash]
    end

    mqtt[MQTT client]

    sensors -- id/sensor/reading --> mqtt
    mqtt --> logging
    mqtt --> strategies
    logging --> storeage
    strategies --> h60
    h60 --> strategies
    h60 --> logging
    storeage2 --> dashboard

```

## Second step
Remove `Strategies` and 

```mermaid
flowchart TD
    sensors[Sensor connection]
    h60[H60 Connection]
    logging([logging thread])
    strategies([strategies thread])
    dashboard([Dashboard thread])

    subgraph Storage
    storage[Storage connection main]
    storage2[Storage connection dash]
    end

    mqtt[MQTT client]

    sensors --> mqtt
    mqtt --> logging
    logging --> storage
    strategies <--> mqtt
    h60 <--> mqtt

    storage2 --> dashboard

```