from os import environ
from dotenv import load_dotenv

load_dotenv()

APP_ROOT_PATH = environ["APP_ROOT_PATH"]

MQTT_TOPIC = f"/measurements/#"
MQTT_HOST = environ["MQTT_HOST"]
MQTT_PORT = int(environ["MQTT_PORT"])
MQTT_USER = environ["MQTT_USER"]
MQTT_PWD = environ["MQTT_PWD"]
MQTT_CLIENT_ID = environ.get("MQTT_CLIENT_ID", default="backend-fastapi")
MQTT_COMMANDS_TOPIC = "/commands"

INFLUX_URL = environ["INFLUX_URL"]
INFLUX_BUCKET = environ["INFLUX_BUCKET"]
INFLUX_ORG = environ["INFLUX_ORG"]
INFLUX_TOKEN = environ["INFLUX_TOKEN"]

SENSORS_NAMES_MAP = {
    "temp_dec": "temperature",
    "aqi": "air_quality"
}
SENSORS_VALUE_PROCESSORS = {
    "temperature": lambda v: v / 10
}
