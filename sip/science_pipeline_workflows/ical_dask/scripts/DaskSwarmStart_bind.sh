#!/bin/bash

# Create overlay network (if required)
NETWORK=ical_sip
docker network create --driver overlay ${NETWORK} --attachable || true

# Create Dask scheduler service and expose ports
docker service create \
    --name scheduler \
    --network ${NETWORK} \
    --publish 8786:8786 \
    --publish 8787:8787 \
    ical_dask_scheduler

# Create Dask worker service adding ARL library as a bind mount
docker service create \
    --name worker \
    --network ${NETWORK} \
    --mount type=bind,source="$(pwd)"/pipelines/sdp_arl,destination=/worker/sdp_arl \
    --env PYTHONPATH=/worker:/worker/sdp_arl \
    --env ARL_DASK_SCHEDULER=scheduler:8786 \
    ical_dask_worker \
    scheduler:8786 --nprocs 8 --nthreads 1
