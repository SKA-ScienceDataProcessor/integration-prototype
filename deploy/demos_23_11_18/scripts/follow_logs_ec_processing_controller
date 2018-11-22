#!/bin/bash
docker service logs --raw --follow "$(docker service ps -q -f desired-state=running sip_ec_processing_controller)"
