"""Program entry point."""

from mqtt_subscriber import MQTTSubscriber

mqtt_subscriber = MQTTSubscriber()
mqtt_subscriber.connect()
mqtt_subscriber.loop_forever()
