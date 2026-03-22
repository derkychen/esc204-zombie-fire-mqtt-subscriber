"""config.py

Loading environment variables and configurations.
"""

import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables
load_dotenv()


@dataclass
class MQTTConfig:
    """URL and credentials for accessing the HiveMQ MQTT broker."""

    BROKER: str = os.getenv("MQTT_BROKER")
    PORT: int = int(os.getenv("MQTT_PORT"))

    USERNAME: str = os.getenv("MQTT_USERNAME")
    PASSWORD: str = os.getenv("MQTT_PASSWORD")

    TOPIC: str = os.getenv("MQTT_TOPIC")


@dataclass
class InfluxDBConfig:
    """URL and credentials for accessing the local InfluxDB database."""

    URL: str = os.getenv("INFLUX_URL")
    TOKEN: str = os.getenv("INFLUX_TOKEN")

    ORG: str = "ignored"  # Parameter required when calling 'post_write'
    DATABASE: str = os.getenv("INFLUX_DATABASE")
