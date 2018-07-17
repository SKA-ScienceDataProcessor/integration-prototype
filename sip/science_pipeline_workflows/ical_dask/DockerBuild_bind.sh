#!/bin/bash

# Script to download the SDP ARL dependency and build Docker images needed
# to deploy the pipeline.


# Download an ARL snapshot (if needed)
if [ ! -d "pipelines/sdp_arl" ]; then
    wget -c -t 10 http://www.mrao.cam.ac.uk/projects/ska/arl/algorithm-reference-library.sip.20180605.tar.gz
    tar xvzf ./algorithm-reference-library.sip.20180605.tar.gz
    mv algorithm-reference-library pipelines/sdp_arl
    rm -f ./algorithm-reference-library.sip.20180605.tar.gz
fi

# Create results folder (if needed)
if [ ! -d "results" ]; then
    mkdir -p results
fi

# Build Docker images
docker build -f dockerfiles/Dockerfile.scheduler -t ical_dask_scheduler .
docker build -f dockerfiles/Dockerfile.worker_bind -t ical_dask_worker .
docker build -f dockerfiles/Dockerfile.pipeline_bind -t ical_dask_pipeline .
