#!/bin/bash

mkdir sip/science_pipeline_workflows/ingest_visibilities/recv_c/build 
cd sip/science_pipeline_workflows/ingest_visibilities/recv_c/build 
cmake -DCOVERALLS=ON -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . --target coveralls
./test/recv_test

