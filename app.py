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

from geolib import geohash

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

    healthkit_data = None
    transformed_data = []

    try:
        healthkit_data = json.loads(request.data)
    except: #pylint:disable=bare-except
        return "Invalid JSON Received", 400

    try:
        logger.info("Ingesting Metrics")
        for metric in healthkit_data.get("data", {}).get("metrics", []):
            number_fields = []
            string_fields = []
            for datapoint in metric["data"]:
                metric_fields = set(datapoint.keys())
                metric_fields.remove("date")
                for mfield in metric_fields:
                    if isinstance(datapoint[mfield], (int, float)):
                        number_fields.append(mfield)
                    else:
                        string_fields.append(mfield)
                point = {
                    "measurement": metric["name"],
                    "time": datapoint["date"],
                    "tags": {str(nfield): str(datapoint[nfield]) for nfield in string_fields},
                    "fields": {str(nfield): float(datapoint[nfield]) for nfield in number_fields}
                }
                transformed_data.append(point)
                number_fields.clear()
                string_fields.clear()

        logger.info("Data Transformation Complete")
        logger.info("Number of data points to write: {len(transformed_data)}")
        logger.info("DB Write Started")

        for i in range(0, len(transformed_data), DATAPOINTS_CHUNK):
            logger.info("DB Writing chunk")
            write_api.write(
                bucket=influx_bucket,
                org=influx_org,
                record=transformed_data[i:i + DATAPOINTS_CHUNK]
            )

        logger.info("DB Metrics Write Complete")
        logger.info("Ingesting Workouts Routes")

        transformed_workout_data = []

        for workout in healthkit_data.get("data", {}).get("workouts", []):
            tags = {
                "id": workout["name"] + "-" + workout["start"] + "-" + workout["end"]
            }
            for gps_point in workout["route"]:
                point = {
                    "measurement": "workouts",
                    "time": gps_point["timestamp"],
                    "tags": tags,
                    "fields": {
                        "lat": gps_point["lat"],
                        "lng": gps_point["lon"],
                        "geohash": geohash.encode(gps_point["lat"], gps_point["lon"], 7),
                    }
                }
                transformed_workout_data.append(point)

            for i in range(0, len(transformed_workout_data), DATAPOINTS_CHUNK):
                logger.info("DB Writing chunk")
                write_api.write(
                    bucket=influx_bucket,
                    org=influx_org,
                    record=transformed_workout_data[i:i + DATAPOINTS_CHUNK]
                )

        logger.info("Ingesting Workouts Complete")
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
    # curl -X POST -d '{ "key: "value" }' http://localhost:5353/collect
