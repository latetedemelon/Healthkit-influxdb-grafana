"""App"""
# pylint:disable=logging-fstring-interpolation
# pylint:disable=invalid-name
# pylint:disable=missing-function-docstring

from dataclasses import dataclass
import json
import logging
import os
import requests

from flask import request, Flask
from health_data.models import metric_from_dict
from geolib import geohash  # If you need geohashing for location data.

# Constants for VictoriaMetrics
VICTORIA_METRICS_URL = os.getenv("VICTORIA_METRICS_URL", "http://localhost:8428/api/v1/import/prometheus")

@dataclass
class AppConfig:
    host: str
    port: int
    debug: bool

host = os.getenv("APP_HOST")
port = os.getenv("APP_PORT")
if port:
    port = int(port)

app_config = AppConfig(
    host=host if host else "0.0.0.0",
    port=port if port else 5353,
    debug=True,
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1000 * 1000  # 64 MB limit for request payloads
app.debug = app_config.debug

def send_to_victoria_metrics(data):
    """
    Send a batch of metrics to VictoriaMetrics using Prometheus-compatible line protocol.
    """
    try:
        response = requests.post(VICTORIA_METRICS_URL, data=data)
        if response.status_code != 200:
            logger.error(f"Error sending data to VictoriaMetrics: {response.status_code} - {response.text}")
        else:
            logger.info("Successfully sent data to VictoriaMetrics")
    except Exception as e:
        logger.error(f"Exception while sending data to VictoriaMetrics: {e}")

@app.route('/collect', methods=['POST', 'GET'])
def collect():
    try:
        logger.info("Request received")
        request_json = json.loads(request.data)
        logger.info(f"Request JSON loaded, keys: {str(request_json.keys())}")
        raw_metrics = request_json["data"]["metrics"]
        del request_json
    except Exception as e:  # Broad exception catching should be used carefully
        logger.error(f"Invalid JSON received: {e}")
        return "Invalid JSON Received", 400

    metrics = []

    while raw_metrics:
        raw_metric = raw_metrics.pop()
        try:
            metrics.append(metric_from_dict(raw_metric))
            logger.info(f"Metric received: {type(metrics[-1])}")
            logger.info(f"Metric data length: {len(metrics[-1].data)}")
        except Exception as e:
            logger.error(f"Error processing metric: {e}")
    
    transformed_data = []
    
    # Transform the metrics to VictoriaMetrics' line protocol format
    for metric in metrics:
        logger.info(f"Logging metric: {type(metric)}, {metric.name}")
        try:
            for point in metric.points():
                line = f'{metric.name}'  # Metric name
                tags = point["tags"]
                fields = point["fields"]
                timestamp = int(point["time"].timestamp()) * 1_000_000_000  # Convert to nanoseconds

                # Append tags to the line
                if tags:
                    line += "," + ",".join([f"{k}={v}" for k, v in tags.items()])

                # Append fields to the line
                field_strings = [f'{k}={v}' for k, v in fields.items()]
                line += f' ' + ','.join(field_strings) + f' {timestamp}'
                transformed_data.append(line)
        except Exception as e:
            logger.error(f"Error transforming metric to VictoriaMetrics format: {e}")

    # Send data in batches to VictoriaMetrics
    if transformed_data:
        try:
            send_to_victoria_metrics("\n".join(transformed_data))
        except Exception as e:
            logger.error(f"Error sending metrics to VictoriaMetrics: {e}")

    return "Success", 200

if __name__ == "__main__":
    logging.basicConfig(filename="app.log", level=logging.DEBUG)
    logging.info("Starting app...")
    app.run(
        host=app_config.host,
        port=app_config.port,
        debug=app_config.debug
    )
