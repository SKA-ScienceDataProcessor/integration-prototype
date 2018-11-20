#!/usr/bin/env bash
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'
echo -e "${RED}---------------------------------------------------------${NC}"
echo -e "${BLUE}Docker ps:${NC}"
docker ps -a -f name='sip*'
echo -e "${RED}---------------------------------------------------------${NC}"
docker stack rm sip
#EXITED_SIP_CONTAINER_IDS="$(docker ps -a -q -f status=exited -f name='sip*')"
#if [[ ! -z "${EXITED_SIP_CONTAINER_IDS}" ]]; then
#    echo "Removing exited SIP containers: ${EXITED_SIP_CONTAINER_IDS}"
#    docker rm "${EXITED_SIP_CONTAINER_IDS}"
#fi
docker network rm sip
docker volume rm sip_tangodb
docker volume rm sip_config_database
