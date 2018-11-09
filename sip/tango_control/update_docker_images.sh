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
    cd ${NAME}
    docker build -t skasip/${NAME}:latest .
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE}Tagging image: skasip/${NAME}:${VERSION}${NC}"
    echo -e "${RED}----------------------------------------------------${NC}"
    docker tag skasip/${NAME}:latest skasip/${NAME}:${VERSION}
    echo -e "${RED}----------------------------------------------------${NC}"
    echo -e "${BLUE}Pushing to dockerhub: skasip/${NAME}:${VERSION}${NC}"
    echo -e "${RED}----------------------------------------------------${NC}"
    docker push skasip/${NAME}:latest
    docker push skasip/${NAME}:${VERSION}
}


VERSION=1.0.0
(build_tango_image docker_base ${VERSION})
(build_tango_image master ${VERSION})
(build_tango_image processing_controller ${VERSION})
(build_tango_image test_device ${VERSION})
(build_tango_image test_client ${VERSION})

