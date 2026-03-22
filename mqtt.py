"""mqtt.py

Defines framework used for MQTT subscription.
"""

from typing import Any
from paho.mqtt.client import (
    Client,
    ConnectFlags,
    DisconnectFlags,
    CallbackAPIVersion,
    MQTTMessage,
)
from paho.mqtt.reasoncodes import ReasonCode
from paho.mqtt.properties import Properties
from config import MQTTConfig
from influxdb import write_payload_from_message


def _on_connect(
    client: Client,
    userdata: Any,
    connect_flags: ConnectFlags,
    reason_code: ReasonCode,
    properties: Properties,
) -> None:
    """Callback upon connection to MQTT broker."""

    if reason_code.is_failure:
        print("Connection rejected by broker.")
        return

    client.subscribe(MQTTConfig.TOPIC)
    print(f"Subscribed to {MQTTConfig.TOPIC}.")


def _on_disconnect(
    client: Client,
    userdata: Any,
    disconnect_flags: DisconnectFlags,
    reason_code: ReasonCode,
    properties: Properties,
) -> None:
    """Callback upon disconnection from MQTT broker."""

    print("Disconnected from broker.")


def _on_message(client: Client, userdata: Any, message: MQTTMessage) -> None:
    """Callback upon reception of message from MQTT broker."""

    try:
        write_payload_from_message(message)
        print(f"Wrote payload from {message.topic}.")

    except Exception as e:
        print(f"Failed to process message from {message.topic}: {str(e)}")


def create_mqtt_client() -> Client:
    """Return an initialised, connected MQTT client."""

    mqtt_client = Client(CallbackAPIVersion.VERSION2)

    # Set callbacks
    mqtt_client.on_connect = _on_connect
    mqtt_client.on_disconnect = _on_disconnect
    mqtt_client.on_message = _on_message

    # Authentication setup
    mqtt_client.username_pw_set(MQTTConfig.USERNAME, MQTTConfig.PASSWORD)
    mqtt_client.tls_set()

    # Connect to MQTT broker
    broker, port = MQTTConfig.BROKER, MQTTConfig.PORT

    mqtt_client.connect(broker, port, keepalive=60)

    return mqtt_client
