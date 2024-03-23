# Readme

This python package provides a simple API endpoint that can collect Apple Health data via the iOS app [Health Auto Export - JSON+CSV](https://apps.apple.com/us/app/health-auto-export-json-csv/id1115567069).

This only collects things like heart rate, active energy, sleep, etc. This currently does not export workouts, symptoms, or ECG data.

## Requirements

- Tested on Python 3.10.
- An iOS device with the app linked above.
- An InfluxDB V2 instance. See `example_make_influxdb.sh` for example script to set up.

## Installation

TODO: Docker install.

1. Clone the repository: `git clone https://github.com/samanthavbarron/Healthkit-influxdb-grafana.git`
2. CD into directory: `cd Healthkit-influxdb-grafana`
3. Make a python venv: `python -m venv .venv`
4. Activate the venv: `source .venv/bin/activate`
5. Install the dependencies: `pip install -r requirements.txt`
6. Install the package: `pip install -e .`
7. Run the tests: `pip install pytest; pytest`
8. Populate `.env` with the environment variables described below. See `example.env` for example, or section below for details.
9. Start the app: `python health_data/app.py`

## Ingest Data

You must have the app linked above installed to ingest data. Once installed, go to Automations -> Automations -> New Automation.

Fill out the fields with the following variables (tweaked to your liking). Anything not listed shouldn't matter:
- Enabled: True
- Notify on Cache Update: False
- Notify When Run: False
- Automation Type: REST API
- URL: `http://APP_HOST:APP_PORT/collect`
- Timeout interval: 60
- Key/Value headers: Leave blank
- Data Type: Health Metrics
- Export Format: JSON

Try running a manual sync by selecting a date range and clicking "Export". If successful, you should see a response value of 200. If you see "An error occured--Could not connect to the server..", then the API endpoint is not accessible from your iOS device. Check your firewall settings, `APP_HOST` and `APP_PORT` variables, etc.

Once this automation is enabled, it should attempt to automatically dump all of your health data into the InfluxDB bucket named `INFLUXDB_BUCKET`.

## Required environment variables
* `APP_HOST`: The IP address or domain where the app should be accessible.
* `APP_PORT`: The port to use for the API endpoint.
* `INFLUXDB_HOST`: The host at which InfluxDB is accessible.
* `INFLUXDB_PORT`: The port at which InfluxDB is accessible.
* `INFLUXDB_ORG`: The org to use for InfluxDB.
* `INFLUXDB_TOKEN`: The token to use for InfluxDB.
* `INFLUXDB_BUCKET`: The bucket in InfluxDB.
