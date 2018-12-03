#!/usr/bin/env bash

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

VERSION="$(python -c "from app.release import __version__; print(__version__)")"

IMAGE=skasip/tango_processing_block
echo -e "${RED}--------------------------------------------------------------${NC}"
echo -e "${BLUE}Building and uploading ${IMAGE} image, version = latest, ${VERSION}"
echo -e "${RED}--------------------------------------------------------------${NC}"

docker build -t ${IMAGE}:latest .
docker tag ${IMAGE}:latest ${IMAGE}:${VERSION}
docker push ${IMAGE}:latest
docker push ${IMAGE}:${VERSION}
