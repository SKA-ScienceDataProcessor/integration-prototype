#!/bin/bash

# Script to run the ICAL Dask workflow data processing container.

docker run \
    --rm \
    --name processing \
    --network ical_sip \
    --env PYTHONPATH=/pipelines:/pipelines/sdp_arl \
    --env ARL_DASK_SCHEDULER=scheduler:8786 \
    -v "$(pwd)"/pipelines/sdp_arl:/pipelines/sdp_arl \
    -v "$(pwd)"/results:/pipelines/results \
    ical_dask_pipeline \
    python3 imaging_processing.py
