#!/usr/bin/env bash
#
# Script which runs Docker container started with an interactive bash prompt
# used for interacting with the Execution Control and Tango Control
# services required for running this demo.
#

TANGO_HOST_ID="$(docker ps -f name=tc_tango_database.1 -f status=running -q)"
docker run --rm -it --network=container:${TANGO_HOST_ID} \
    --network=container:${TANGO_HOST_ID} \
    -e REDIS_HOST=ec_config_database \
    skasip/workflow_demo_client:latest

