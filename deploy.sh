#!/usr/bin/env bash
docker stack deploy -c deploy/demos_23_11_18/local/docker-compose.yml sip
docker stack services sip

# initialise the database? - could be done with docker run ... (see itango)
