#!/usr/bin/env bash

docker service logs --raw --follow "$(docker service ps -q -f desired-state=running sip_tango_subarray)"
