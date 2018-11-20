#!/usr/bin/env bash
docker service logs "$(docker service ps -f desired-state=running tango_tango_master -q)"
