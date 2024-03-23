"""App"""
# pylint:disable=logging-fstring-interpolation
# pylint:disable=invalid-name
# pylint:disable=missing-function-docstring

import json
import logging

from flask import request, Flask

from health_data.models import metric_from_dict, Metric, SleepAnalysisMetric

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
        metrics = request_json["data"]["metrics"]
    except: #pylint:disable=bare-except
        return "Invalid JSON Received", 400

    for metric in metrics:
        try:
            metric = metric_from_dict(metric)
            logger.info(f"Metric received: {type(metric)}")
            logger.info(f"Metric data length: {len(metric.data)}")
        except:
            logger.exception("Error processing metric")

        logger.info("Logging data to InfluxDB...")

    return "Success", 200

if __name__ == "__main__":
    app.run(
        host=app_config.host,
        port=app_config.port,
        debug=app_config.debug
    )
