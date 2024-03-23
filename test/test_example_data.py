"""This test module reads in the example data from `./data.json` and 
sends it to the `/collect` endpoint of the Flask app. It then checks
the response status code and the response message to ensure that the
data was received successfully.
"""

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

EXAMPLE_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data.json"
)

class TestExampleData(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()
    
    def test_example_data(self):
        data = json.load(open(EXAMPLE_DATA_PATH))
        response = self.client.post("/collect", json=data)
        self.assertEqual(response.status_code, 200)

class TestModel(unittest.TestCase):

    def setUp(self):
        metrics = json.load(open(EXAMPLE_DATA_PATH))["data"]["metrics"]
        
        self.raw_sleep_metric = None
        self.raw_metrics = []
        for metric in metrics:
            if metric["name"] == "sleep_analysis":
                self.raw_sleep_metric = copy(metric)
            else:
                self.raw_metrics.append(copy(metric))
        
        if self.raw_sleep_metric is None:
            raise ValueError("No sleep_analysis metric found in data.json")
    
    def test_metric_from_dict(self):
        self.assertGreater(len(self.raw_metrics), 0)
        for raw_metric in self.raw_metrics:
            metric = metric_from_dict(raw_metric)
            self.assertIsInstance(metric, Metric)
            self.assertGreaterEqual(len(metric.data), 1)
            self.assertIsInstance(metric.data[0], DataRecord)
        
        sleep_metric = metric_from_dict(self.raw_sleep_metric)
        self.assertIsInstance(sleep_metric, SleepAnalysisMetric)
        self.assertIsInstance(sleep_metric.data[0], SleepAnalysisRecord)

if __name__ == "__main__":
    unittest.main()
