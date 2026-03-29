# ESC204 Team 0112C Zombie Fire MQTT Subscriber

Team 0112C: Atharv KudChadKar, Charlie Martinez, Derek Chen, Han Fang, Oscar Low, Rooney Cheung

This repository contains an MQTT subscriber that writes data to a local InfluxDB instance, as well as a JSON for a Grafana dashboard that visualises this data.

## Prerequisites

You are on macOS and you have installed:

* `brew`
* `python3`
* `uv`
* `influxdb`
* `grafana` (installed with `brew`)

## Setup

Clone the repository:

```sh
git clone https://github.com/derkychen/esc204-zombie-fire-mqtt-subscriber.git
```

Inside the project directory, run the `uv sync` to install dependencies:

## Run subscriber

```sh
chmod +x run_mqtt_subscriber.sh # Allow this script ot be run (you only need to run this command once)
./run_mqtt_subscriber.sh
```
