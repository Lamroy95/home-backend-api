from typing import List, Optional
import logging

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client import InfluxDBClient

from app import config
from app.models.entities import Commands
from app.mqtt import MQTTApp
from app.models.responses import Place, Sensor, Room
from app import db

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    client_id=config.MQTT_CLIENT_ID,
    topic=config.MQTT_TOPIC
)


@app.on_event("startup")
def on_startup():
    mqtt.start(host=config.MQTT_HOST, port=config.MQTT_PORT)


@app.on_event("shutdown")
def on_shutdown():
    mqtt.stop()
    influx.close()


@app.get("/measurements/places/", response_model=List[Place])
async def get_places(
        include_values: bool = True,
        last_n_minutes: Optional[int] = Query(5, gt=0),
        influx_client: InfluxDBClient = Depends(lambda: influx),
):
    """
    Get list of all available places.
    """
    try:
        places = db.get_all_places(influx_client, include_values, last_n_minutes)
    except ValueError as e:
        raise HTTPException(404, str(e))

    return places


@app.post("/command/{command_name}/{param}")
async def set_fan_level(command_name: Commands, param: int, mqtt_app=Depends(lambda: mqtt)):
    mqtt_app.publish(
        topic=f"{config.MQTT_COMMANDS_TOPIC}/{command_name.value}",
        value=f"{param}"
    )
    return {"ok": True}
