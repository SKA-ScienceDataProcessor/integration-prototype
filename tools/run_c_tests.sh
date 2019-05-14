#!/bin/bash

mkdir sip/science_pipeline_workflows/ingest_visibilities/recv_c/build 
cd sip/science_pipeline_workflows/ingest_visibilities/recv_c/build 
cmake -DCOVERALLS=ON -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_CPPCHECK:FILEPATH=cppcheck .. 
cmake --build .
./test/recv_test
cmake --build . --target coveralls
