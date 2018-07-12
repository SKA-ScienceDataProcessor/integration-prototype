#!/bin/bash

# docker run --rm -it \
#     --name modeling \
#     --network ical_sip \
#     --env ARL_DASK_SCHEDULER=scheduler:8786 \
#     --env PYTHONPATH=/pipelines:/pipelines/sdp_arl \
#     -v "$(pwd)"/pipelines:/pipelines \
#     --entrypoint python3 \
#     ical_dask_pipeline \
#     /pipelines/imaging_modeling.py

docker run --rm -it \
    --name modeling \
    --network ical_sip \
    --env ARL_DASK_SCHEDULER=scheduler:8786 \
    --env PYTHONPATH=/pipelines:/pipelines/sdp_arl \
    -v "$(pwd)"/pipelines:/pipelines \
    --entrypoint /bin/bash \
    ical_dask_pipeline

# python3 /pipelines/imaging_modeling.py
