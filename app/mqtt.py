from typing import Optional

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, WriteOptions

from app import loggers
from app.models import Measurement
from app.influxdb.api import write_measurement


class MQTTApp:
    def __init__(
            self,
            user: str,
            password: str,
            influx: InfluxDBClient,
            influx_bucket: str,
            client_id: Optional[str] = None,
    ):
        self.client = mqtt.Client(client_id=client_id, clean_session=False)
        self.client.username_pw_set(username=user, password=password)
        self.influx = influx
        self.bucket = influx_bucket

        self._setup_handlers()

    def _setup_handlers(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        loggers.mqtt.info("Connected to MQTT broker")

    def on_disconnect(self, client: mqtt.Client, userdata, rc):
        loggers.mqtt.info("Disconnected from MQTT broker")

    def on_subscribe(self, client: mqtt.Client, userdata, mid, granted_qos):
        loggers.mqtt.info(f"Subscribed")

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        value = msg.payload.decode('utf-8')
        loggers.mqtt.error(msg.topic)
        _, place, room, sensor_name = msg.topic.rsplit("/", maxsplit=3)
        loggers.mqtt.info(f"Recieved value from \"{sensor_name}\": {value}")
        m = Measurement(value=value, name=sensor_name, place=place, room=room)
        write_measurement(client=self.influx, bucket=self.bucket, measurement=m)

    def subscribe(self, topic: str):
        self.client.subscribe(topic)

    def start(self, host, port):
        self.client.connect(host=host, port=port)
        self.client.loop_start()

    def stop(self):
        self.client.disconnect()
