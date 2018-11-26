#!/bin/bash
# Script to build and upload the log_spammer image.

function build_and_publish_image() {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    VERSION="$(python -c "from _version import __version__; print(__version__)")"
    echo -e "${RED}--------------------------------------------------------------${NC}"
    echo -e "${BLUE}Building and uploading log_spammer image, version = latest, ${VERSION}"
    echo -e "${RED}--------------------------------------------------------------${NC}"
    docker build -t skasip/log_spammer:latest .
    docker tag skasip/log_spammer:latest skasip/log_spammer:"${VERSION}"
    docker push skasip/log_spammer:latest
    docker push skasip/log_spammer:"${VERSION}"
}

build_and_publish_image
