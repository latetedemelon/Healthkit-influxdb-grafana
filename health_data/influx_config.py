"""Module to store the InfluxDB configuration data."""

import os
from dataclasses import dataclass

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


@dataclass
class InfluxConfig:
    host: str
    port: str
    org: str
    bucket: str
    token: str
    
    def url(self):
        return f"http://{self.host}:{self.port}"

influx_config = InfluxConfig(
    host = str(os.getenv('INFLUXDB_HOST')),
    port = str(os.getenv('INFLUXDB_PORT')),
    org = str(os.getenv('INFLUXDB_ORG')),
    bucket = str(os.getenv('INFLUXDB_BUCKET')),
    token = str(os.getenv('INFLUXDB_TOKEN')),
)

influx_client = InfluxDBClient(
    url=influx_config.url(),
    token=influx_config.token,
    org=influx_config.org,
)
influx_write_api = influx_client.write_api(write_options=SYNCHRONOUS)
