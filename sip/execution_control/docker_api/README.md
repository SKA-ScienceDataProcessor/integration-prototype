# SKA SDP SIP Docker Swarm Client API

## Introduction

This package contains a client library for interfacing with the Docker engine
for creating, deleting and inspecting Docker Swarm services as well as 
managing Docker Swarm nodes.

This library is intended to be used by other SKA SDP SIP Execution Control
services, in particular the Processing Block Controller.

## Quick-start

Install with:

```bash
pip3 install -U skasip-docker-swarm
```

Example usage:

```python
from sip_docker_swarm import DockerSwarmClient
DOCKER_SWARM = DockerSwarmClient()
DOCKER_SWARM.get_service_list()
```

## Testing

Linting and unit test are run automatically by SIP CI/CD system but can also be 
run manually from the docker_api code directory with:

```bash
pytest --pylint --docstyle --codestyle -s -v --pylint-rcfile=../../../.pylintrc .
```

or run the following command from the top level directory

```bash
./tools/run_tests.sh sip/execution_control/docker_api/sip_docker_swarm    
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
