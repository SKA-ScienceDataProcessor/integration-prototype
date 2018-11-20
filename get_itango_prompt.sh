#!/usr/bin/env bash
TANGO_HOST_ID="$(docker ps -f name=tango_database.1 -f status=running -q)"
IMAGE=skasip/tango_interactive_client:1.1.2
docker run -it --rm --network=container:${TANGO_HOST_ID} \
    -v "$(pwd)"/deploy/demos_23_11_18/data:/home/sip/data \
    "${IMAGE}"
