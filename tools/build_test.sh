#!/bin/bash

set -euo pipefail

mkdir sip/science_pipeline_workflows/ingest_visibilities/recv_c/build
cd sip/science_pipeline_workflows/ingest_visibilities/recv_c/build
#cmake ..

# Configure
cmake -DCODE_COVERAGE=ON -DCMAKE_BUILD_TYPE=Debug ..
cmake --build . --config Debug -- -j $(nproc)
# cmake --build .

# Test
ctest -j $(nproc) --output-on-failure
# ./test/recv_test