#!/usr/bin/env bash
TANGO_HOST_ID="$(docker ps -f name=tango_database.1 -f status=running -q)"
IMAGE=skasip/tango_interactive_client:1.1.2
docker run -it --rm --network=container:${TANGO_HOST_ID} \
    -e REDIS_HOST=config_database \
    -v "$(pwd)"/deploy/demos_23_11_18/data:/home/sip/data \
    -v "$(pwd)"/deploy/demos_23_11_18/itango_utils:/home/sip/itango_utils \
    "${IMAGE}"
