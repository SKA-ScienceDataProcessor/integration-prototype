#!/bin/bash

# Bash script to trawl through SIP code folders run PyLint


run_pylint () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    PYLINT_LOG=temp_pylint.log
    rm -f "$PYLINT_LOG" || true
    echo -e "${RED}$1${NC}"
    find "$1" -name "*.py" | while read -r line; do
        pylint -s n -r n -f colorized "$line" > ${PYLINT_LOG} 2>/dev/null
        if [ -s "${PYLINT_LOG}" ]; then
            echo -e "  ${BLUE}$line${NC}"
            awk '{ print "     " $0 }' ${PYLINT_LOG}
        fi
    done
    rm -f "$PYLINT_LOG" || true
}

if [ $# -eq 0 ]; then
  run_pylint "emulators"
  run_pylint "sip"
else
  for path in "$@"; do
    run_pylint "$path"
  done
fi
