#!/bin/bash

# Script to create the Dask EE services needed to run the ICAL workflow.

# Create overlay network (if required)
NETWORK=ical_sip
docker network create --driver overlay ${NETWORK} --attachable

# Create Dask scheduler service and expose ports
docker service create \
    --name scheduler \
    --network ${NETWORK} \
    --publish 8786:8786 \
    --publish 8787:8787 \
    vlad7235/ical_dask_scheduler:latest

# Create Dask worker service adding ARL library as a bind mount
docker service create \
    --name worker \
    --network ${NETWORK} \
    --mount type=bind,source="$(pwd)"/pipelines/sdp_arl,destination=/worker/sdp_arl \
    --env ARL_DASK_SCHEDULER=scheduler:8786 \
    --env PYTHONPATH=/worker/sdp_arl \
    --replicas 2 \
    vlad7235/ical_dask_worker:latest \
    scheduler:8786 --nprocs 2 --nthreads 1 --memory-limit 2GB
