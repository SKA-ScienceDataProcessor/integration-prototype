#!/bin/bash

# Bash script to trawl through SIP code folders and print contents of
# requirement files.


list_requirements () {
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    echo -e "${RED}$1${NC}"
    find "$1" -name "req*.txt" | while read -r line; do
        if [ -s "$line" ]; then
            echo -e "  ${BLUE}$line${NC}"
            awk '{ print "     " $0 }' "$line"
        fi
    done
}

echo $#

if [ $# -eq 0 ]; then
  list_requirements "emulators"
  list_requirements "sip"
else
  for path in "$@"; do
    list_requirements "$path"
  done
fi
