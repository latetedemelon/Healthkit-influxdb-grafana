"""Module to store the VictoriaMetrics configuration and data handling."""

import os
import logging
import requests
from typing import Sequence

logger = logging.getLogger(__name__)

# VictoriaMetrics configuration
VICTORIA_METRICS_URL = os.getenv("VICTORIA_METRICS_URL", "http://localhost:8428/api/v1/import/prometheus")

def send_to_victoria_metrics(data: str):
    """
    Send a batch of metrics to VictoriaMetrics using Prometheus-compatible line protocol.
    
    Args:
        data (str): The metrics data in line protocol format to be sent to VictoriaMetrics.
    """
    try:
        response = requests.post(VICTORIA_METRICS_URL, data=data)
        if response.status_code != 200:
            logger.error(f"Error sending data to VictoriaMetrics: {response.status_code} - {response.text}")
        else:
            logger.info("Successfully sent data to VictoriaMetrics")
    except Exception as e:
        logger.error(f"Exception while sending data to VictoriaMetrics: {e}")

def write_points(points: Sequence[str]):
    """
    Send the points data to VictoriaMetrics. The points should be in Prometheus line protocol format.
    
    Args:
        points (Sequence[str]): A list of metric data points to be sent to VictoriaMetrics.
    """
    if not points:
        logger.warning("No points to write to VictoriaMetrics.")
        return

    # Prepare the data to be sent
    data = "\n".join(points)
    
    # Send the data to VictoriaMetrics
    send_to_victoria_metrics(data)
