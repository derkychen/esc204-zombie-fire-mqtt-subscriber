"""main.py

Program entry point.
"""

from mqtt import create_mqtt_client

# Create MQTT subscriber and listen indefinitely
mqtt_client = create_mqtt_client()
mqtt_client.loop_forever()
