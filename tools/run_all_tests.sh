#!/usr/bin/env bash
# Run all linters and unit tests.
./tools/run_tests.sh sip/execution_framework_interface/docker_api || exit
./tools/run_tests.sh sip/execution_framework_interface/docker_compose_generator  || exit
./tools/run_tests.sh sip/science_pipeline_workflows/ical_dask  || exit
./tools/run_tests.sh sip/platform/logging  || exit
./tools/run_tests.sh sip/execution_control/configuration_db  || exit
