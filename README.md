# ESC204 Team 0112C Zombie Fire MQTT Subscriber

This repository contains MQTT subscriber-side data processing and storage (InfluxDB) and visualisation (Grafana).

## Prerequisites

You are on macOS and you have installed:

* `brew`
* `python3`
* `influxdb`
* `grafana`

## Setup

Clone the repository:

```sh
git clone https://github.com/derkychen/esc204-zombie-fire-mqtt-subscriber.git
```

Inside the project directory, run the following to install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run subscriber

```sh
chmod +x run_mqtt_subscriber.sh # Give permissions to run the script (only need to run once)
./run_mqtt_subscriber.sh
```
