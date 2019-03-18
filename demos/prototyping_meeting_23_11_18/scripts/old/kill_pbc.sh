#!/usr/bin/env bash

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

NAME="sip_pbc"


echo -e "${BLUE}docker ps -f name='${NAME}*'${NC}"
echo -e "---------------------------------------"
CONTAINERS="$(docker ps -f name=${NAME}*)"
echo -e "${CONTAINERS}"
echo -e "---------------------------------------"
CONTAINER_IDS="$(docker ps -q -f name=${NAME}*)"

echo -e "${BLUE}Killing container:"
for CONTAINER_ID in ${CONTAINER_IDS[@]}; do
    echo -e "${RED}- ${CONTAINER_ID}${NC}"
    docker kill "${CONTAINER_ID}"

    echo -e "${BLUE}* Waiting for service ${NAME} to restart${NC}"
    docker service ls -f name=${NAME}
    while true; do
        SERVICE_ID="$(docker service ps -q -f desired-state=running "${NAME}")"
        if [[ ! -z "${SERVICE_ID}" ]]; then
            echo -e "-- ${BLUE} Service started!! ID = ${SERVICE_ID}${NC}"
            sleep "1"
            docker service ls -f name=${NAME}
            break
        fi
    done

done

echo -e ""
echo -e "---------------------------------------"
echo -e "${BLUE}Killing Mock workflow stage services:${NC}"
echo -e "---------------------------------------"
docker service rm stage1 stage2 stage3

