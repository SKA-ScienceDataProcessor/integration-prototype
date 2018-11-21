#!/usr/bin/env bash
# Script to get an interactive prompt in a named Tango Service container.
#
# FIXME(BMo) This only works if there is one container ID per service.

function get_prompt () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    NAME="tango_${1}"
    COMMAND="${2}"
    CONTAINER_ID="$(docker ps -q -f name=${NAME}.1 -f status=running)"
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE}Getting prompt for ${NAME}:"
    echo -e "${BLUE}  Container ID = ${CONTAINER_ID}"
    echo -e "${BLUE}  docker exec -it -w /home/sip/${NAME} ${CONTAINER_ID} ${COMMAND}"
    echo -e "${RED}----------------------------------------------------${NC}"
    docker exec -it -w /home/sip/${NAME} "${CONTAINER_ID}" "${COMMAND}"
}

if [[ $# -ne 0 ]]; then
    echo "$#"
    echo "Usage: $0"
    exit 1
fi

PS3='Please select an option : '
options=(
    "interactive_client"
    "master_client"
    "itango"
    "master"
    "processing_block"
    "subarray"
    "quit"
)
select opt in "${options[@]}"
do
    case "${opt}" in
        "interactive_client")
            (get_prompt "${opt}" "/bin/bash")
            break
            ;;
        "master_client")
            (get_prompt "${opt}" "/bin/bash")
            break
            ;;
        "itango")
            (get_prompt "interactive_client" "itango3")
            break
            ;;
        "master")
            (get_prompt "${opt}" "/bin/bash")
            break
            ;;
        "processing_block")
            (get_prompt "${opt}" "/bin/bash")
            break
            ;;
        "subarray")
            (get_prompt "${opt}" "/bin/bash")
            break
            ;;
        "quit")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done
