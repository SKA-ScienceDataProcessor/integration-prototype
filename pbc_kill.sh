#!/bin/bash
docker service rm stage1 stage2 stage3
docker kill "$(docker ps -q -f name=pc_pbc)"
