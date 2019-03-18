#!/bin/bash
# Script to build and upload a docker image.

function build_and_publish_image() {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    VERSION="1.0.0"
    #VERSION="$(python -c "import app; print(app.__version__)")"
    IMAGE=skasip/ec_alert_manager
    echo -e "${RED}--------------------------------------------------------------${NC}"
    echo -e "${BLUE}Building and uploading ${IMAGE} image, version = latest, ${VERSION}"
    echo -e "${RED}--------------------------------------------------------------${NC}"
    docker build -t ${IMAGE}:latest .
    docker tag ${IMAGE}:latest ${IMAGE}:"${VERSION}"
    docker push ${IMAGE}:latest
    docker push ${IMAGE}:"${VERSION}"
}

build_and_publish_image
