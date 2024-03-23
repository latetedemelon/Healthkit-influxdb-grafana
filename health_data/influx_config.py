"""Module to store the InfluxDB configuration data."""

import os
from typing import Optional, Sequence
from dataclasses import dataclass

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


@dataclass
class InfluxConfig:
    host: Optional[str]
    port: Optional[str]
    org: Optional[str]
    bucket: Optional[str]
    token: Optional[str]

    def url(self):
        return f"http://{self.host}:{self.port}"

influx_config = InfluxConfig(
    host=os.getenv('INFLUXDB_HOST'),
    port=os.getenv('INFLUXDB_PORT'),
    org=os.getenv('INFLUXDB_ORG'),
    bucket=os.getenv('INFLUXDB_BUCKET'),
    token=os.getenv('INFLUXDB_TOKEN'),
)

influx_client = InfluxDBClient(
    url=influx_config.url(),
    token=influx_config.token,
    org=influx_config.org,
    timeout=20_000,
)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def write_points(points: Sequence[Point]):
    influx_write_api.write(
        bucket=influx_config.bucket,
        record=points,
        batch_size=10_000,
    )
