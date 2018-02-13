#!/bin/bash

# Bash script to trawl through SIP code folders run PyCodeStyle


run_pycodestyle () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    OUT_LOG=temp_pycodestyle.log
    rm -f "OUT_LOG" || true
    echo -e "${RED}$1${NC}"
    find "$1" -name "*.py" | while read -r line; do
        pycodestyle "$line" > ${OUT_LOG} 2>/dev/null
        if [ -s "${OUT_LOG}" ]; then
            echo -e "  ${BLUE}$line${NC}"
            awk '{ print "     " $0 }' ${OUT_LOG}
        fi
    done
    rm -f "$OUT_LOG" || true
}

if [ $# -eq 0 ]; then
  run_pycodestyle "emulators"
  run_pycodestyle "sip"
else
  for path in "$@"; do
    run_pycodestyle "$path"
  done
fi
