#!/usr/bin/env bash


RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}* Killing service tango_master.1${NC}"
docker kill "$(docker ps -f name=tango_master.1 -f status=running -q)"

echo -e "${RED}* Waiting for service to restart${NC}"
while true; do
    SERVICE_ID="$(docker service ps -f desired-state=running tango_tango_master -q)"
    if [[ ! -z "${SERVICE_ID}" ]]; then
        echo -e "-- ${BLUE} Service started!! ID = ${SERVICE_ID}${NC}"
        break
    fi
done
