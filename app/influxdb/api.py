from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

from app.models import Measurement
from app import loggers


def write_measurement(
        client: InfluxDBClient,
        bucket: str,
        measurement: Measurement
):
    point = Point(measurement.name).tag("place", measurement.place)\
                                   .field("sensor_value", measurement.value)
    with client.write_api(write_options=ASYNCHRONOUS) as wapi:
        r = wapi.write(bucket=bucket, record=point)
        r.get()
    loggers.influx.info(f"Written point \"{point.to_line_protocol()}\"")
