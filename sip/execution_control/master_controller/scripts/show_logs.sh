#!/usr/bin/env bash
CONTAINER_ID="$(docker service  ps -q --filter desired-state=running mc_master_controller)"
docker service logs "${CONTAINER_ID}"
