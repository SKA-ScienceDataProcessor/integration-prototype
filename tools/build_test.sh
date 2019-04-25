#!/bin/bash

mkdir sip/science_pipeline_workflows/ingest_visibilities/recv_c/build
cd sip/science_pipeline_workflows/ingest_visibilities/recv_c/build
cmake ..
cmake --build .
./test/recv_test