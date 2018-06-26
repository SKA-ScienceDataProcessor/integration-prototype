# Very Simple example workflow deployment using Docker

This is a slightly more complicated workflow than `dask_workflow_test_01`
in that the workflow is deployed using a modified worker container
which includes additional workflow scripts and dependencies.

## Quick-start

Build the workflow worker container:

```bash
docker build -t skasip/dask_workflow_test_02 .
```

### Deploy to Docker Swarm using host networking

Notes:

- **IMPORTANT** When using host networking, Docker swarm does not support
  service discovery from the overlay network. As such the HOST (and PORT)
  of the scheduler must be configured via the environment varaible
  `DASK_SCHEDULER_HOST`.

To deploy the Dask cluster (1 scheduler + 1 worker):

```bash
docker stack deploy -c docker-compose.hostnet.ee.yml dask
```

And to run the workflow:

```bash
docker stack deploy -c docker-compose.hostnet.workflow.yml workflow
```

This could also be run on a control node natively using, as long as this
script invocation can connect to the Dask scheduler deamon.

```bash
python3 -m workflow
```

To clean up:

```bash
docker stack rm dask
```

```bash
docker stack rm workflow
```

### Deploy to Docker Swarm using overlay networking

Create a overlay network:

```bash
docker network create --driver overlay --attachable workflow_02
```

Start the dask cluster:

```bash
docker stack deploy -c docker-compose.overlay.ee.yml dask
```

Start the workflow:

```bash
docker stack deploy -c docker-compose.overlay.workflow.yml workflow
```

Clean up:

```bash
docker stack rm dask workflow
docker network prune -f
```