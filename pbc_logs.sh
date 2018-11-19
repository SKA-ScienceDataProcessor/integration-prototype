#!/bin/bash

docker logs --follow "$(docker ps -q -f name=pbc_pbc)"
