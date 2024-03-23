#!/bin/bash
set -e

docker volume rm influxdb2-data || :
docker volume rm influxdb2-config || :

docker volume create influxdb2-data
docker volume create influxdb2-config

USERNAME=admin
PASSWORD=password1234
ORG=my_org_name
BUCKET=my_bucket_name
PORT=8086

docker run -d \
  --name influxdb2 \
  --publish $PORT:8086 \
  --restart unless-stopped \
  --mount type=volume,source=influxdb2-data,target=/var/lib/influxdb2 \
  --mount type=volume,source=influxdb2-config,target=/etc/influxdb2 \
  --env DOCKER_INFLUXDB_INIT_MODE=setup \
  --env DOCKER_INFLUXDB_INIT_USERNAME=$USERNAME \
  --env DOCKER_INFLUXDB_INIT_PASSWORD=$PASSWORD \
  --env DOCKER_INFLUXDB_INIT_ORG=$ORG \
  --env DOCKER_INFLUXDB_INIT_BUCKET=$BUCKET \
  influxdb:2

