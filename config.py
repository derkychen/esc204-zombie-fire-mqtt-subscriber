"""Loading of environment variables and configurations."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class MQTTConfig:
    """URL and credentials for accessing the HiveMQ MQTT broker."""

    BROKER: str = os.getenv("MQTT_BROKER")
    PORT: int = int(os.getenv("MQTT_PORT"))

    USERNAME: str = os.getenv("MQTT_USERNAME")
    PASSWORD: str = os.getenv("MQTT_PASSWORD")

    TOPICS: list[str] = tuple(os.getenv("MQTT_TOPICS").split(","))


@dataclass
class InfluxDBConfig:
    """URL and credentials for accessing the local InfluxDB database."""

    URL: str = os.getenv("INFLUXDB_URL")
    TOKEN: str = os.getenv("INFLUXDB_TOKEN")

    ORG: str = "ignored"  # Parameter required when calling 'post_write'
    DATABASE: str = os.getenv("INFLUXDB_DATABASE")
