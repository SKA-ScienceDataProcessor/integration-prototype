#!/usr/bin/env bash

function build_tango_image () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    NAME=tango_${1}
    VERSION=${2}
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE}Building image: skasip/${NAME}:latest${NC}"
    echo -e "${RED}----------------------------------------------------${NC}"
    cd "${NAME}" || return
    docker build -t skasip/"${NAME}":latest .
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE}Tagging image: skasip/${NAME}:${VERSION}${NC}"
    echo -e "${RED}----------------------------------------------------${NC}"
    docker tag skasip/"${NAME}":latest skasip/"${NAME}":"${VERSION}"
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE}Pushing to dockerhub: skasip/${NAME}:${VERSION}${NC}"
    echo -e "${RED}----------------------------------------------------${NC}"
    docker push skasip/"${NAME}":latest
    docker push skasip/"${NAME}":"${VERSION}"
}


if [ $# -ne 1 ]; then
    echo $#
    echo "Usage: $0 VERSION"
    exit 1
fi

VERSION=$1
PS3='Please select an option : '
options=(
    "master"
    "processing_controller"
    "subarray"
    "interactive_client"
    "docker_base"
    "mysql"
    "database"
    "all"
    "quit"
)
select opt in "${options[@]}"
do
    case $opt in
        "master")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "processing_controller")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "subarray")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "interactive_client")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "docker_base")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "mysql")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "database")
            (build_tango_image "${opt}" "${VERSION}")
            break
            ;;
        "all")
            for value in "${options[@]}";
            do
                if [[ ${value} != "all" && ${value} != "quit" ]]; then
                   (build_tango_image "${value}" "${VERSION}")
                fi
            done
            break
            ;;
        "quit")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done
