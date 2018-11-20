#!/usr/bin/env bash

docker service logs --follow "$(docker service ps -q -f desired-state=running sip_master_controller)"
