# SKA SDP SIP Processing Block Controller

Library and Celery worker image for executing Processing Block workflows 
within the SDP SIP prototype code. This is implemented as a set 
of [Celery](http://www.celeryproject.org/) tasks which can be used to 
asynchronously execute SIP Processing Block workflows on a Processing
Block Controller (*Celery Worker*) instance.

## Library installation

```bash
pip install skasip-pbc
```

## Starting a containerised PBC instance

For the Processing Block Controller to function, a *Redis Database* instance
must be created, which provides the role of the *Celery Broker* and 
*Execution Control Configuration Database*. Once this is available,
a *Processing Block Controller (Celery Worker)* can be started. 

For the *Redis Database*m a standard redis container can be started (eg. using 
the official [`redis:5.0.1-alpine`](https://hub.docker.com/r/library/redis/) 
image). *The Processing Block Controller Celery worker* can be started using 
the image [`skasip/processing_block_controller`](https://cloud.docker.com/u/skasip/repository/docker/skasip/processing_block_controller).  

A Docker Compose file (`docker-compose.dev.yml`) is provided in this folder 
for starting a Redis instance and a PBC Celery worker. This can be used with
the following command: 

```bash
docker stack deploy -c docker-compose.dev.yml pbc
``` 


## Typical usage

**Note:** Requires a *Celery Worker*, *Celery Broker*, and a
*SKA SIP Execution Control Configuration Database* instance are running 
(see above)!  

```python
# coding: utf-8
"""Example SIP PBC usage."""
import sip_pbc

# Get the PBC version.
result = sip_pbc.version.delay()
version = result.get(timeout=1)
print(version)

# Execute a PB workflow.
result = sip_pbc.execute_processing_block.delay(pb_id='...')
``` 

