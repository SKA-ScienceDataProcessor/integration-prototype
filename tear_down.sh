#!/usr/bin/env bash
docker ps -a -f name='sip*'
docker stack rm sip
#EXITED_SIP_CONTAINER_IDS="$(docker ps -a -q -f status=exited -f name='sip*')"
#if [[ ! -z "${EXITED_SIP_CONTAINER_IDS}" ]]; then
#    echo "Removing exited SIP containers: ${EXITED_SIP_CONTAINER_IDS}"
#    docker rm "${EXITED_SIP_CONTAINER_IDS}"
#fi
docker network rm sip
docker volume rm sip_tangodb
docker volume rm sip_config_database
