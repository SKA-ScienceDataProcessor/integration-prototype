#!/bin/bash

cd sip/science_pipeline_workflows/ingest_visibilities/
cppcheck recv_c/ -i gtest/ --enable=warning,portability,style
mkdir recv_c/build
cd recv_c/build

cmake -DENABLE_ASAN=ON ..
make
./test/recv_test

cd .. && rm -r -f build && mkdir build && cd build
cmake -DCOVERALLS=ON -DCMAKE_BUILD_TYPE=Debug ..
make
make coveralls

ctest -T memcheck
