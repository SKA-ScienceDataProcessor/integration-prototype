# Docker Client API

## Introduction

Docker is a tool tha can package an application and its containers in a virtual 
container. Docker Swarm is a clustering and scheduling tool for Docker container.


The client library is written as a high level functions for use by various 
Execution Control Services. The client lets you run docker commands from within
Python - create services, delete services, manage nodes etc

## Quick-start

## Utility Scripts

## Testing

Linting and unit test are run automatically by SIP CI/CD system but can also be 
run manually from the docker_api code directory with:

py.test --pylint --codestyle -s -v --pylint-rcfile=../../../.pylintrc .

## TODO

* Need to add exception into the functions
* Replace and add Log to the script
* Write README file
* depends_on is not enabled -> Need to look into this
* Need to setup the enviorment variables
* Unit test for update_node function

