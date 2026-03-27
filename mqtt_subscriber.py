"""Defines utilities used for MQTT subscription.

The main purpose of this module is to expose the 'MQTTSubscriber' wrapper class
for subscription to MQTT topic(s) and automatic writing to InfluxDB.
"""

from typing import Any

from paho.mqtt.client import (
    MQTT_ERR_SUCCESS,
    CallbackAPIVersion,
    Client,
    ConnectFlags,
    DisconnectFlags,
    MQTTMessage,
)
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

from config import MQTTConfig
from influxdb_utils import InfluxDBUtils


class MQTTSubscriber:
    """MQTT Subscriber wrapper class."""

    def __init__(self):
        """Initialise MQTT client with relevant attributes."""
        self._subscribed_topics = {}

        self._influx_db_utils = InfluxDBUtils()
        self._mqtt_client = Client(CallbackAPIVersion.VERSION2)

        # Set callbacks
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_message = self._on_message

        # Authentication setup
        self._mqtt_client.username_pw_set(
            MQTTConfig.USERNAME, MQTTConfig.PASSWORD
        )
        self._mqtt_client.tls_set()

    def connect(self) -> None:
        """Connect to MQTT broker."""
        self._mqtt_client.connect(
            MQTTConfig.BROKER, MQTTConfig.PORT, keepalive=60
        )

    def loop_forever(self) -> None:
        """Start network loop."""
        self._mqtt_client.loop_forever()

    def _on_connect(
        self,
        client: Client,
        userdata: Any,
        connect_flags: ConnectFlags,
        reason_code: ReasonCode,
        properties: Properties,
    ) -> None:
        """Callback upon connection to MQTT broker, subscribes.

        Args:
            client: The Client instance for this callback.
            userdata: Private user data as set in Client().
            connect_flags: Flags for the connection.
            reason_code: Connection reason code received from the broker.
            properties: MQTT v5.0 properties recieved from the broker.
        """
        if reason_code.is_failure:
            print("Connection rejected by broker.")
            return

        # Attempt to subscribe to topic upon connection
        for topic in MQTTConfig.TOPICS:
            result, _ = client.subscribe(topic)

            if result == MQTT_ERR_SUCCESS:
                print(f"Subscribed to {topic}.")
            else:
                print("Failed to send subscription request.")

    def _on_disconnect(
        self,
        client: Client,
        userdata: Any,
        disconnect_flags: DisconnectFlags,
        reason_code: ReasonCode,
        properties: Properties,
    ) -> None:
        """Callback upon disconnection from MQTT broker.

        Args:
            client: Client instance for this callback.
            userdata: Private user data as set in Client().
            disconnect_flags: Flags for the disconnection.
            reason_code: Disconnection reason code possibly received from the
                broker.
            properties: MQTT v5.0 properties recieved from the broker.
        """
        print("Disconnected from broker.")

    def _on_message(
        self, client: Client, userdata: Any, message: MQTTMessage
    ) -> None:
        """Callback upon reception of message from MQTT broker, writes payload.

        Args:
            client: Client instance for this callback.
            userdata: Private user data as set in Client().
            message: Received message.
        """
        try:
            self._influx_db_utils.write_payload_from_message(message)
            print(f"Wrote payload from {message.topic}.")

        except Exception as e:
            print(f"Failed to process message from {message.topic}: {str(e)}")
