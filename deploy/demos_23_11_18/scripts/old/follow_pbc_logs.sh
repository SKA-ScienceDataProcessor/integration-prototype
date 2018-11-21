#!/bin/bash
docker service logs --raw --follow "$(docker service ps -q -f desired-state=running sip_processing_block_controller)"
