from typing import List
import logging

from fastapi import FastAPI, HTTPException
from influxdb_client import InfluxDBClient

from app import config
from app.mqtt import MQTTApp
from app.models import Place, Sensor, Room
from app import db

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
)

app = FastAPI()
influx = InfluxDBClient(
    url=config.INFLUX_URL,
    token=config.INFLUX_TOKEN,
    org=config.INFLUX_ORG
)
mqtt = MQTTApp(
    user=config.MQTT_USER,
    password=config.MQTT_PWD,
    influx=influx,
    influx_bucket=config.INFLUX_BUCKET,
    client_id=config.MQTT_CLIENT_ID
)


@app.on_event("startup")
def on_startup():
    mqtt.start(host=config.MQTT_HOST, port=config.MQTT_PORT)
    mqtt.subscribe(topic=config.MQTT_TOPIC)


@app.on_event("shutdown")
def on_shutdown():
    mqtt.stop()
    influx.close()


@app.get("/measurements/places/", response_model=List[Place])
async def get_places():
    """
    Get list of all available places
    """
    places = db.get_all_places()
    return places


@app.get("/measurements/places/{place_name}/", response_model=List[Room])
async def get_rooms(place_name: str):
    """
    Get list of all rooms in place
    """
    try:
        rooms = db.get_rooms(place_name)
    except ValueError as e:
        raise HTTPException(404, str(e))

    return rooms


@app.get("/measurements/places/{place_name}/{room_name}", response_model=List[Sensor])
async def get_sensors(place_name: str, room_name):
    """
    Get list of all sensors in room
    """
    try:
        sensors = db.get_sensors(place_name, room_name)
    except ValueError as e:
        raise HTTPException(404, str(e))

    return sensors
