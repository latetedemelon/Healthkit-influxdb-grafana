"""Tests for the app and models modules."""

import unittest
from copy import copy
import json
import os

from health_data.app import app
from health_data.models import (
    metric_from_dict,
    Metric,
    SleepAnalysisMetric,
    DataRecord,
    SleepAnalysisRecord,
)

from influxdb_client import Point

EXAMPLE_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data.json"
)

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()
    
    def test_example_data(self):
        """Test that the request can be sensibly received and processed.
        This test will still pass even if the data is not written to InfluxDB.
        """
        data = json.load(open(EXAMPLE_DATA_PATH))
        response = self.client.post("/collect", json=data)
        self.assertEqual(response.status_code, 200)

class TestModels(unittest.TestCase):

    def setUp(self):
        metrics = json.load(open(EXAMPLE_DATA_PATH))["data"]["metrics"]

        self.raw_metrics = []
        for metric in metrics:
            if metric["name"] == "sleep_analysis":
                self.raw_sleep_metric = copy(metric)
            else:
                self.raw_metrics.append(copy(metric))
        try:
            self.raw_sleep_metric
        except AttributeError:
            raise ValueError("No sleep_analysis metric found in data.json")

    def test_metric_from_dict(self):
        """Test that we can get a Metric object from a dictionary."""
        self.assertGreater(len(self.raw_metrics), 0)
        for raw_metric in self.raw_metrics:
            metric = metric_from_dict(raw_metric)
            self.assertIsInstance(metric, Metric)
            self.assertGreaterEqual(len(metric.data), 1)
            self.assertIsInstance(metric.data[0], DataRecord)

        sleep_metric = metric_from_dict(self.raw_sleep_metric)
        self.assertIsInstance(sleep_metric, SleepAnalysisMetric)
        self.assertIsInstance(sleep_metric.data[0], SleepAnalysisRecord)

    def test_metric_points(self):
        """Test that we can get a list of Point objects from a Metric object."""
        sleep_metric = metric_from_dict(self.raw_sleep_metric)
        points = list(sleep_metric.points())
        self.assertGreater(len(points), 0)
        for point in points:
            self.assertIsInstance(point, Point)

if __name__ == "__main__":
    unittest.main()
