# Docker Swarm Client API

## Introduction

The SIP Execution Framework provides a Docker Client Python API to run
docker services by various Execution Control Service components.

The client library is written as a of Python modules which are structured as a 
set of higher level modules use by various Execution Control Services. 
The client lets you run docker commands from within Python - create services, 
delete services, manage nodes etc

## Quick-start

Install with:

```bash
pip3 install -U skasip-docker-swarm
```

Example usage:

```python
from sip_docker_swarm import DockerClient
DC = DockerClient()
```

## Testing

Linting and unit test are run automatically by SIP CI/CD system but can also be 
run manually from the docker_api code directory with:

```bash
pytest --pylint --docstyle --codestyle -s -v --pylint-rcfile=../../../.pylintrc .
```

## TODO

* Need to add exception into the functions
* Add Log to the script
* depends_on is not enabled -> Need to look into this
* Need to setup the environment variables
* Unit test for update_node function
* Figure out how to validate compose files
* While it is useful to test that service exists, it mighe be even better to test
that the service is running as well
