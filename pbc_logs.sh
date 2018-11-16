#!/bin/bash

docker logs --follow "$(docker ps -q -f name=pc_pbc)"
