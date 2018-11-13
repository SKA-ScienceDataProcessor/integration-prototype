#!/usr/bin/env bash

function get_prompt () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    NAME=tango_${1}
    VERSION=${2}
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE} docker exec -it $(docker ps -q -f name=${NAME}) /bin/bash"
    echo -e "${RED}----------------------------------------------------${NC}"
    docker exec -it $(docker ps -q -f name=${NAME}) /bin/bash
}


if [ $# -ne 0 ]; then
    echo $#
    echo "Usage: $0"
    exit 1
fi

VERSION=$1
PS3='Please select an option : '
options=(
    "interactive_client"
    "itango"
    "master"
    "processing_controller"
    "subarray"
    "quit"
)
select opt in "${options[@]}"
do
    case $opt in
        "interactive_client")
            (get_prompt "${opt}")
            break
            ;;
        "itango")
            docker exec -it $(docker ps -q -f name="interactive_client") itango3
            break
            ;;
        "master")
            (get_prompt "${opt}")
            break
            ;;
        "processing_controller")
            (get_prompt "${opt}")
            break
            ;;
        "subarray")
            (get_prompt "${opt}")
            break
            ;;
        "quit")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done
