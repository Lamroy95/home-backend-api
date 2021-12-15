from contextlib import suppress
from functools import partial

from app.models.responses import Place, Room, Sensor, SensorValue, Fan
from app.influxdb.api import get_measurements, get_measurement

all_places = [
    Place(
        name="home",
        rooms=[Room(name="room1", sensors=[
            Sensor(id="temperature", name="Temperature", unit="°C", gauge=False),
            Sensor(id="humidity", name="Humidity", unit="%", min=0, max=100, normal=40, gauge=True),
            Sensor(id="air_quality", name="Air polution", min=0, max=500, normal=0, gauge=True),
            Sensor(id="bright", name="Illuminance", unit="lux", min=0, max=200, gauge=False),
        ])]
    )
]


def get_all_places(influx_client, include_values, last_n_minutes):
    if not include_values:
        return all_places
    for place in all_places:
        for room in place.rooms:
            # with suppress(ValueError):
            room.fan = get_fan(influx_client, place.name, room.name)

            for sensor in room.sensors:
                sensor.values = get_sensor_values(
                    influx_client,
                    place.name,
                    room.name,
                    sensor.id,
                    last_n_minutes
                )
    return all_places


def get_sensor_values(influx_client, place_name, room_name, sensor_id, last_n_minutes):
    points = get_measurements(
        client=influx_client,
        measurement=sensor_id,
        place=place_name,
        room=room_name,
        last_n_minutes=last_n_minutes
    )
    return [SensorValue(**p) for p in points]


def get_fan(influx_client, place_name, room_name):
    helper = partial(get_measurement, client=influx_client, place=place_name, room=room_name)
    mode = helper(measurement="mode")
    motor_speed = helper(measurement="motor1_speed")
    filter_days_left = helper(measurement="filter1_life")
    fan_level = helper(measurement="favorite_level")

    return Fan(
        mode=mode["value"],
        motor_speed=motor_speed["value"],
        filter_days_left=filter_days_left["value"],
        manual_fan_level=fan_level["value"]
    )
