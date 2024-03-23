"""App"""
# pylint:disable=logging-fstring-interpolation
# pylint:disable=invalid-name
# pylint:disable=missing-function-docstring

import json
import logging

from flask import request, Flask

from health_data.models import metric_from_dict
from health_data.influx_config import write_points

from dataclasses import dataclass


@dataclass
class AppConfig:
    host: str
    port: int
    chunks: int
    debug: bool

app_config = AppConfig(
    host = "0.0.0.0",
    port = 5353,
    chunks = 80000,
    debug = True,
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.debug = app_config.debug

@app.route('/collect', methods=['POST', 'GET'])
def collect():
    try:
        logger.info("Request received")
        request_json = json.loads(request.data)
        logger.info(f"Request JSON loaded, keys: {str(request_json.keys())}")
        raw_metrics = request_json["data"]["metrics"]
        del request_json
    except: #pylint:disable=bare-except
        return "Invalid JSON Received", 400

    metrics = []

    while raw_metrics:
        raw_metric = raw_metrics.pop()
        try:
            metrics.append(metric_from_dict(raw_metric))
            logger.info(f"Metric received: {type(metrics[-1])}")
            logger.info(f"Metric data length: {len(metrics[-1].data)}")
        except:
            logger.error(f"Error processing metric")
    
    for metric in metrics:
        logger.info(f"Logging metric: {type(metric)}")
        try:
            write_points(metric.points())
        except:
            logger.error(f"Error writing metric to InfluxDB: {type(metric)}")

    return "Success", 200

if __name__ == "__main__":
    app.run(
        host=app_config.host,
        port=app_config.port,
        debug=app_config.debug
    )
