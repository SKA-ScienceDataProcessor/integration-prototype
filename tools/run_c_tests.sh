#!/bin/bash

cd sip/science_pipeline_workflows/ingest_visibilities/
cppcheck recv_c/ -i gtest/ --enable=warning,portability,style
mkdir recv_c/build
cd recv_c/build
cmake -DCOVERALLS=ON -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . 
./test/recv_test
cmake --build . --target coveralls
