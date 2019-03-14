#!/bin/bash
# Script to build and upload a docker image.

function build_and_publish_image() {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    VERSION="$(cat VERSION)"
    IMAGE=skasip/vis_recv_c
    echo -e "${RED}--------------------------------------------------------------${NC}"
    echo -e "${BLUE}Building and uploading ${IMAGE} image, version = latest, ${VERSION}"
    echo -e "${RED}--------------------------------------------------------------${NC}"
    docker build -t ${IMAGE}:latest .
    docker tag ${IMAGE}:latest ${IMAGE}:"${VERSION}"
    docker push ${IMAGE}:latest
    docker push ${IMAGE}:"${VERSION}"
}

build_and_publish_image
