#

## Quickstart

```bash
docker build skasip/dask_workflow_test_02 .
```

```bash
docker stack deploy -c docker-compose.yml dask
```


```bash
python3 -m workflow
```


















# Placeholder for containerised Dask workflow example

This can probably be based on the official Dask Dockerfile found at
<https://github.com/dask/dask-docker/tree/master/base> with
dependencies for the workflow installed into the container. In this particular
example this is `astropy` and the `workflow_module` functions in this folder.

The container needs to have the worker and scheduler configured appropriately
for the node size or worker model (ie expected number of workers per node).
This might be possible using Docker configuration to pass in a json config
to Containers?

Need to work out how to configure Dask with the right network.
Need to work out the way Dask needs to interact with the buffer ie what volume
mounts to provide to containers.

The workflow code itself does not need to be installed into the container?


<https://dask.pydata.org/en/latest/setup/hpc.html#using-a-shared-network-file-system-and-a-job-scheduler>

- Dask is then deployed as a scheduler container and a set of worker containers
- The workflow script connects to the scheduler as a client an issues
  tasks.


If the interface application which obtains a client cant get the list of
futures to cancel, we may need a special wrapper that tracks the futures
as part of the interface code when it runs the workflow.