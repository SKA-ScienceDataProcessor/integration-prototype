#!/usr/bin/env bash

docker pull skasip/tango_master:1.0.6
docker pull skasip/tango_docker_base:1.0.5
docker pull skasip/tango_database:1.0.4
docker pull skasip/tango_mysql:1.0.3
docker pull skasip/tango_interactive_client:1.0.6

docker pull redis:4.0.6-alpine
docker pull rediscommander/redis-commander:latest
