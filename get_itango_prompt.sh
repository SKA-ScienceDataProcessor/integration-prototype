#!/usr/bin/env bash
TANGO_HOST_ID="$(docker ps -f name=tango_database.1 -f status=running -q)"
IMAGE=skasip/tango_interactive_client:1.0.7
docker run -it --rm --network=container:${TANGO_HOST_ID} "${IMAGE}"
