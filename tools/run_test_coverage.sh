#!/usr/bin/env bash
TEST_DIRS="$@"
CMD="python -m pytest --cov-append --cov-branch "
for TEST_DIR in ${TEST_DIRS[@]}; do
    CMD="${CMD}--cov=${TEST_DIR} "
done
CMD="${CMD} --rootdir=. "
for TEST_DIR in ${TEST_DIRS[@]}; do
    CMD="${CMD}${TEST_DIR} "
done

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}----------------------------------------------------------${NC}"
echo -e "${BLUE}Running test coverage analysis:"
echo -e "${BLUE}${CMD}"
echo -e "${RED}----------------------------------------------------------${NC}"
eval "${CMD}"
