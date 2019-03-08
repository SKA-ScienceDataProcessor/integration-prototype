#!/bin/bash
# Run tests and linters for specified directory.
#
# Usage:
#   ./tools/run_tests.sh <directory> [--test-only] [pytest flags]
#
# Example:
#   ./tools/run_tests.sh sip/execution_control/configuration_db \
#        --test-only -x -k test_workflow_definitions
#

Usage() {
   printf "Usage: %s <directory> [--test-only] [pytest flags]\n" "$0"
   exit 1
}

# Colours used in printing output
RED=$(tput setaf 1)
BLUE=$(tput setaf 4)
NC=$(tput sgr0)


[[ -n $1 ]] && [[ -d $1 ]] || { 
   printf "directory not provided or does not exist\n"
   Usage 
}

DIR=$1
shift
printf "%s* DIR=%s'%s'\n" "$RED" "$NC" "$DIR"

if [[ -n $1 ]] && [[ $1 = --test-only ]]
then
    shift
    full_test_options=
else
    full_test_options="
    --pylint 
    --pylint-rcfile=.pylintrc 
    --codestyle 
    --docstyle 
    --cov-config=./setup.cfg 
    --cov-append 
    --cov-branch 
    --no-cov-on-fail 
    --cov=${DIR}
    "
fi

if [[ $# -ge 1 ]]
then
    prefix_options=$'-m pytest -s -v \
    --rootdir=.'
    printf "%s------------------------------------------------------\n" \
            "$RED"
    printf "* OPTIONS=%s%s\n" "$NC" "$*"
else
     prefix_options=$'-m pytest -s -vv 
    --rootdir=.'
fi
printf "%s------------------------------------------------------\n" \
            "$RED" 
printf "%sRunning tests:\n   python3 %s %s %s %s\n" \
             "$BLUE" "$prefix_options" "$full_test_options" "$*" "$DIR"
printf "%s------------------------------------------------------%s\n" \
            "$RED" "$NC"

python3 $prefix_options $full_test_options $* $DIR
