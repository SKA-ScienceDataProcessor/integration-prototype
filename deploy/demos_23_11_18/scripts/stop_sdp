#!/usr/bin/env bash

source "$(cd "$(dirname "$0")" ; pwd -P)"/incl.sh

# Remove the SIP stack
eval_cmd "docker stack rm sip"

# Print list of any remaining SIP containers
if [[ ! -z "$(docker ps -a -q -f name='sip*')" ]]; then
    eval_cmd "docker ps -a -f name='sip*'"
fi

# Docker rm any exited containers.
IDS="$(docker ps -a -q -f status=exited)"
IDS="${IDS//$'\n'/ }"
if [[ ! -z ${IDS} ]]; then
    docker rm ${IDS}
fi

# Remove the SIP network
if [[ ! -z "$(docker network ls -q -f name=sip)" ]]; then
    echo ""
    eval_cmd "docker network rm sip"
fi

# Remove SIP docker volumes
docker volume prune -f
#VOLUMES=(sip_tangodb sip_tango_mysql sip_pbc_backend sip_pbc_broker sip_config_database)
#for VOLUME in ${VOLUMES[@]}; do
#    VOLUME_ID=$(docker volume ls -q -f name='${VOLUME}')
#    echo "Checking if ${VOLUME} exists: |${VOLUME_ID}|"
#    if [[ ! -z $(docker volume ls -q -f name='${VOLUME}') ]]; then
#        echo "Yes - attempting to remove it."
#        docker volume rm ${VOLUME}
#    else:
#        echo "No."
#    fi
#done
