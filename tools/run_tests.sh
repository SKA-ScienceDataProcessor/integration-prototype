#!/usr/bin/env bash
# Run tests and linters for specified directory.
#
# Usage:
#   ./tools/run_tests.sh <directory> [--test-only] [pytest flags]
#
# Example:
#   ./tools/run_tests.sh sip/execution_control/configuration_db \
#        --test-only -x -k test_workflow_definitions
#
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

DIR="$1"
echo -e "${RED}* DIR=${NC}'${DIR}'"
OPTIONS=("${@:2}")
if [[ ! -z "${OPTIONS}" && "${OPTIONS[0]}" == "--test-only" ]]; then
    OPTIONS="${OPTIONS[@]:1}"
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${RED}* OPTIONS=${NC}'${OPTIONS}'"
    CMD="python3 -m pytest -s -v \
    --rootdir=. \
    ${OPTIONS[*]} \
    ${DIR}"
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${BLUE}Running tests:"
    echo -e "${BLUE}${CMD}"
    echo -e "${RED}------------------------------------------------------${NC}"
elif [[ ! -z "${OPTIONS}" ]]; then
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${RED}* OPTIONS=${NC}'${OPTIONS}'"
    CMD="python3 -m pytest -s -v \
    --rootdir=. \
    --pylint \
    --pylint-rcfile=.pylintrc \
    --codestyle \
    --docstyle \
    --cov-config=./setup.cfg \
    --cov-append \
    --cov-branch \
    --no-cov-on-fail \
    --cov=${DIR} \
    ${OPTIONS[*]} \
    ${DIR}"
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${BLUE}Running tests:"
    echo -e "${BLUE}${CMD}"
    echo -e "${RED}------------------------------------------------------${NC}"
else
    CMD="python3 -m pytest -s -vv \
    --rootdir=. \
    --pylint \
    --pylint-rcfile=.pylintrc \
    --codestyle \
    --docstyle \
    --cov-config=./setup.cfg \
    --cov-branch \
    --cov-append \
    --no-cov-on-fail \
    --cov=${DIR} \
    ${DIR}"
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${BLUE}Running tests:"
    echo -e "${BLUE}${CMD}"
    echo -e "${RED}------------------------------------------------------${NC}"
fi
eval ${CMD}
