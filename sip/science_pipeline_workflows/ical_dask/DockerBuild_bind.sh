#!/bin/bash

# Script to download the SDP ARL dependency and build Docker images needed
# to deploy the pipeline.


# Download an ARL snapshot (if needed)
ARL_DIR=pipelines/sdp_arl
ARL_TARBALL=algorithm-reference-library.sip.20180820.tar.gz
echo $ARL_DIR
echo $ARL_TARBALL
#echo "Removing ARL_DIR and all content"
#if [ -d "$ARL_DIR" ]; then rm -Rf "$ARL_DIR"; fi    
if [ ! -d "$ARL_DIR" ]; then
    echo "Downloading ARL tarball"
    wget -c -t 10 "http://www.mrao.cam.ac.uk/projects/ska/arl/$ARL_TARBALL"
    tar xvzf "./$ARL_TARBALL"
    mv algorithm-reference-library pipelines/sdp_arl
    rm -f "./$ARL_TARBALL"
fi

# Create results folder (if needed)
if [ ! -d "results" ]; then
    mkdir -p results
fi

# Build Docker images
docker build -f dockerfiles/Dockerfile.scheduler -t ical_dask_scheduler .
docker build -f dockerfiles/Dockerfile.worker_bind -t ical_dask_worker .
docker build -f dockerfiles/Dockerfile.pipeline_bind -t ical_dask_pipeline .
