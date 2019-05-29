#!/bin/bash

cd sip/science_pipeline_workflows/ingest_visibilities/
cppcheck recv_c/ -i gtest/ --enable=warning,portability,style
mkdir recv_c/build
cd recv_c/build
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_COMPILER=clang++ -DADDRESS_SANITIZER=On -DCOVERALLS=ON ..
make
./test/recv_test
cmake --build . --target coveralls
