#!/usr/bin/env bash
SIP_IMAGE_IDS="$(docker image ls --filter=reference='skasip/*' -q)"
docker image rm --force "${SIP_IMAGE_IDS}"
