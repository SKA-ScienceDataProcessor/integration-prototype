#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)

cd sip/science_pipeline_workflows/ingest_visibilities/
echo -e "\n ${bold}*** Running Cpp Check *** ${normal} \n"
cppcheck recv_c/ -i gtest/ --enable=warning,portability,style
mkdir recv_c/build
cd recv_c/build

echo -e "\n ${bold}*** Running Coveralls *** ${normal} \n"
cmake -DCOVERALLS=ON -DCMAKE_BUILD_TYPE=Debug ..
make
make coveralls

echo -e "\n ${bold}*** Running Valgrind using Ctest testing tool *** ${normal} \n"
ctest -T memcheck

echo -e "\n ${bold}*** Running Undefined Behaviour Sanitizer *** ${normal} \n"
cd .. && rm -r -f build && mkdir build && cd build
cmake -DENABLE_USAN=ON ..
make
./test/recv_test

echo -e "\n ${bold}*** Running Threading Sanitizer *** ${normal} \n"
cd .. && rm -r -f build && mkdir build && cd build
cmake -DENABLE_TSAN=ON ..
make
./test/recv_test

echo -e "\n ${bold}*** Running Address Sanitizer *** ${normal} \n"
cd .. && rm -r -f build && mkdir build && cd build
cmake -DENABLE_ASAN=ON ..
make
./test/recv_test

