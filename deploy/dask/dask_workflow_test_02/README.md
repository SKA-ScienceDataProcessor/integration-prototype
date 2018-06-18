# Very Simple example workflow deployment using Docker

This is a slightly more complicated workflow than `dask_workflow_test_01`
in that the workflow is deployed using a modified worker container
which includes additional workflow scripts and dependencies.


## Quick-start

Build the workflow worker container:

```bash
docker build -t skasip/dask_workflow_test_02 .
```

Deploy the Dask cluster (1 scheduler + 1 worker):

```bash
docker stack deploy -c docker-compose.yml Dask
```

Run the workflow:

```bash
python3 -m workflow
```

Clean up:

```bash
docker stack rm dask
```