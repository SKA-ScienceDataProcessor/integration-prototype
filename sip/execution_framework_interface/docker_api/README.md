# Docker Client API

## Introduction

The SIP Execution Framework provides a Docker Client Python API to run
docker services by various Execution Control Service components.

The client library is written as a of Python modules which are structured as a 
set of higher level modules use by various Execution Control Services. 
The client lets you run docker commands from within Python - create services, 
delete services, manage nodes etc

## Quick-start

To use the client, simply copy the client script to the service directory.

import the client and initialise the client.

```bash
from ..docker_client import DockerClient

DC = DockerClient()
```

## Testing

Linting and unit test are run automatically by SIP CI/CD system but can also be 
run manually from the docker_api code directory with:

py.test --pylint --codestyle -s -v --pylint-rcfile=../../../.pylintrc .

## TODO

* Need to add exception into the functions
* Replace and add Log to the script
* Write README file
* depends_on is not enabled -> Need to look into this
* Need to setup the environment variables
* Unit test for update_node function
* Figure out how to validate compose files

