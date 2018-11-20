#!/usr/bin/env bash
# Run tests and linters for specified directory.
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

DIR="$1"
echo -e "${RED}* DIR=${NC}'${DIR}'"
OPTIONS="${@:2}"
if [[ ! -z "${OPTIONS}" ]]; then
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${RED}* OPTIONS=${NC}'${OPTIONS}'"
    CMD="python3 -m pytest -s -v --codestyle --docstyle --pylint ${OPTIONS} \
    --pylint-rcfile=.pylintrc --rootdir=. \"${DIR}\""
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${BLUE}Running tests:"
    echo -e "${BLUE}${CMD}"
    echo -e "${RED}------------------------------------------------------${NC}"
else
    CMD="python3 -m pytest -s -v --codestyle --docstyle --pylint \
    --pylint-rcfile=.pylintrc --rootdir=. \"${DIR}\""
    echo -e "${RED}------------------------------------------------------${NC}"
    echo -e "${BLUE}Running tests:"
    echo -e "${BLUE}${CMD}"
    echo -e "${RED}------------------------------------------------------${NC}"
fi
eval ${CMD}
