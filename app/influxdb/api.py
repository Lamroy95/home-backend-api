import datetime
from typing import Optional

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

from app.models.entities import Measurement
from app import loggers, config


def write_measurement(
        client: InfluxDBClient,
        measurement: Measurement,
        bucket: Optional[str] = config.INFLUX_BUCKET,
):
    point = Point(measurement.name).tag("place", measurement.place)\
                                   .tag("room", measurement.room)\
                                   .field("sensor_value", measurement.value)
    with client.write_api(write_options=ASYNCHRONOUS) as wapi:
        r = wapi.write(bucket=bucket, record=point)
        r.get()
    loggers.influx.info(f"Written point \"{point.to_line_protocol()}\"")


def get_measurements(
        client: InfluxDBClient,
        measurement: str,
        place: str,
        room: str,
        last_n_minutes: int,
        bucket: Optional[str] = config.INFLUX_BUCKET,
):
    query_params = {
        "_bucket": bucket,
        "_start": datetime.timedelta(minutes=-last_n_minutes),
        "_measurement": measurement,
        "_place": place,
        "_room": room,
    }
    query = """
    from(bucket:_bucket) |> range(start: _start)
        |> filter(fn: (r) => r["_measurement"] == _measurement)
        |> filter(fn: (r) => r["place"] == _place)
        |> filter(fn: (r) => r["room"] == _room)
        |> sort(columns: ["_time"], desc: true)
    """
    qapi = client.query_api()
    tables = qapi.query(query, params=query_params)
    if not tables:
        return []
    table = tables[0]
    return [
        {"timestamp": int(r["_time"].timestamp()), "value": r["_value"]}
        for r in table.records
    ]


def get_measurement(
        client: InfluxDBClient,
        measurement: str,
        place: str,
        room: str,
        bucket: Optional[str] = config.INFLUX_BUCKET,
):
    query_params = {
        "_bucket": bucket,
        "_measurement": measurement,
        "_place": place,
        "_room": room,
    }
    query = """
    from(bucket:_bucket) |> range(start: -10s)
        |> filter(fn: (r) => r["_measurement"] == _measurement)
        |> filter(fn: (r) => r["place"] == _place)
        |> filter(fn: (r) => r["room"] == _room)
        |> sort(columns: ["_time"], desc: true)
    """
    qapi = client.query_api()
    tables = qapi.query(query, params=query_params)
    if not tables or not tables[0].records:
        raise ValueError("Values not found")
    last_record = tables[0].records[0]
    return {"timestamp": int(last_record["_time"].timestamp()), "value": last_record["_value"]}
