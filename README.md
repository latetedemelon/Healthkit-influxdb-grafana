# Readme

This is a fork of Ivo's [original project](https://github.com/ivailop7/Healthkit-influxdb-grafana) and [blog post](https://www.ivaylopavlov.com/charting-apple-healthkit-data-in-grafana/#.YyN_lS-B3yI).

All I've done is added some things to set up with Docker and update the InfluxDB stuff to V2. Very much still a work in progress. If you want to try it out yourself, you'll need to specify the following environment variables, e.g. in a `.env` file or in `docker-compose.yml`.
* `INFLUXDB_HOST`
* `INFLUXDB_PORT`
* `INFLUXDB_ORG`
* `INFLUXDB_TOKEN`
* `INFLUXDB_BUCKET`
