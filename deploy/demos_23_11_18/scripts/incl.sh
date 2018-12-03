#!/usr/bin/env bash

RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

function echo_red {
    echo -e "${RED}${1}${NC}"
}

function echo_blue {
    echo -e "${BLUE}${1}${NC}"
}

function blue_line {
    echo -e "${BLUE}-----------------------------------------------------${NC}"
}

function red_line {
    echo -e "${RED}-----------------------------------------------------${NC}"
}

function line {
    echo -e "-----------------------------------------------------${NC}"
}

function eval_cmd {
    CMD="$1"
    echo_blue "* CMD: ${CMD}"
    red_line
    eval "${CMD}"
    echo ""
}

