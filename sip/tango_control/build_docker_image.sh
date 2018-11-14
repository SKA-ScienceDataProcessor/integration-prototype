#!/usr/bin/env bash
# Script build and upload Tango docker images.

function build_tango_image () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    NAME=tango_${1}
    VERSION=$(python -c "from tango_${opt}._version import __version__; print(__version__)")
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


if [ $# -ne 0 ]; then
    echo $#
    echo "Usage: $0"
    exit 1
fi

VERSION=$1
PS3='Please select an option : '
options=(
    "docker_base"
    "master"
    "processing_block"
    "subarray"
    "interactive_client"
    "mysql"
    "database"
    "quit"
)




select opt in "${options[@]}"
do
    case $opt in
        "master")
            (build_tango_image "${opt}")
            break
            ;;
        "processing_block")
            (build_tango_image "${opt}")
            break
            ;;
        "subarray")
            (build_tango_image "${opt}")
            break
            ;;
        "interactive_client")
            (build_tango_image "${opt}")
            break
            ;;
        "docker_base")
            (build_tango_image "${opt}")
            break
            ;;
        "mysql")
            (build_tango_image "${opt}")
            break
            ;;
        "database")
            (build_tango_image "${opt}")
            break
            ;;
        "quit")
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done
