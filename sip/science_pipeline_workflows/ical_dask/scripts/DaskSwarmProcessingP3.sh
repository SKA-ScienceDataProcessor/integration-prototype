#!/bin/bash

# Script to run the ICAL Dask workflow data processing service.

docker service create \
    --name sip_processing \
    --network ical_sip  \
    --env PYTHONPATH=/pipelines:/pipelines/sdp_arl \
    --env ARL_DASK_SCHEDULER=scheduler:8786 \
    --mount type=bind,source=/var/mnt/ceph/vlad/pipelines,destination=/pipelines \
    --mount type=bind,source=/var/mnt/ceph/vlad/sdp_arl,destination=/pipelines/sdp_arl \
    --mount type=bind,source=/var/mnt/ceph/vlad/results,destination=/pipelines/results \
    --replicas 1 \
    --restart-condition=none \
    vlad7235/ical_dask_pipeline:latest \
    python3 imaging_processing.py 
    


