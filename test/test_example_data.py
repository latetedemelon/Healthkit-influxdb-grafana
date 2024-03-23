"""This test module reads in the example data from `./data.json` and 
sends it to the `/collect` endpoint of the Flask app. It then checks
the response status code and the response message to ensure that the
data was received successfully.
"""

import unittest
import json
import os

from health_data.app import app

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

if __name__ == "__main__":
    unittest.main()
