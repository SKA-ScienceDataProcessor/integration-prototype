#!/usr/bin/env bash

source "$(cd "$(dirname "$0")" ; pwd -P)"/incl.sh

NAME="sip_tc_tango_master"
CONTAINER_IDS="$(docker ps -q -f name=${NAME}.1*)"
for CONTAINER_ID in ${CONTAINER_IDS[@]}; do
    docker kill "${CONTAINER_ID}"
    while true; do
        SERVICE_ID="$(docker service ps -q -f desired-state=running "${NAME}")"
        if [[ ! -z "${SERVICE_ID}" ]]; then
            sleep 0.1
            break
        fi
    done
done
sleep 2
docker service logs --raw --follow "$(docker service ps -q -f desired-state=running ${NAME})"
