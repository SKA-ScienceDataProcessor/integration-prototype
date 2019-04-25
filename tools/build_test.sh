#!/bin/bash

mkdir sip/science_pipeline_workflows/ingest_visibilities/recv_c/build
cd sip/science_pipeline_workflows/ingest_visibilities/recv_c/build
cmake ..
cmake --build .
./test/recv_test
gcov-5 sip/science_pipeline_workflows/ingest_visibilities/recv_c/src/*.{c,h}
gcov-5 sip/science_pipeline_workflows/ingest_visibilities/recv_c/test/Tests.cpp