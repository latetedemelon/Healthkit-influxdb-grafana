"""App"""
# pylint:disable=logging-fstring-interpolation
# pylint:disable=invalid-name
# pylint:disable=missing-function-docstring

import json
import os
import sys
import socket
import logging

from flask import request, Flask

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from health_data.models import metric_from_dict, Metric, SleepAnalysisMetric

influx_host = str(os.getenv('INFLUXDB_HOST'))
influx_port = str(os.getenv('INFLUXDB_PORT'))
influx_org = str(os.getenv('INFLUXDB_ORG'))
influx_bucket = str(os.getenv('INFLUXDB_BUCKET'))
influx_token = str(os.getenv('INFLUXDB_TOKEN'))

app_host = "0.0.0.0"
app_port = 5353

DATAPOINTS_CHUNK = 80000

logger = logging.getLogger("console-output")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
app.debug = True

influx_url = f"http://{influx_host}:{influx_port}"
client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

@app.route('/collect', methods=['POST', 'GET'])
def collect():
    logger.info("Request received")

    try:
        healthkit_data = json.loads(request.data)
    except: #pylint:disable=bare-except
        return "Invalid JSON Received", 400

    try:
        logger.info("Starting ingestion...")
    except: # pylint: disable=bare-except
        logger.exception("Caught Exception. See stacktrace for details.")
        return "Server Error", 500

    return "Success", 200

if __name__ == "__main__":
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    logger.info(f"InfluxDB URL: {influx_url}")
    logger.info(f"InfluxDB Org: {influx_org}")
    logger.info(f"InfluxDB Bucket: {influx_bucket}")
    logger.info(f"Local Network Endpoint: http://{ip_address}/collect")
    app.run(host=app_host, port=app_port)