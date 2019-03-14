#!/usr/bin/env bash
IMAGE=skasiid/tango_prompt:latest
TANGO_HOST_ID="$(docker ps -f name=tc_tango_database.1 -f status=running -q)"

docker run -it --rm \
    --network=container:"${TANGO_HOST_ID}" \
    -e REDIS_HOST=ec_config_database \
    --entrypoint=itango3 \
    "${IMAGE}"
