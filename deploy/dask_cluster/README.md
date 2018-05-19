# Docker (Swarm) Dask cluster deployment

Experimental [Docker Compose](https://docs.docker.com/compose/) script to deploy a test [Dask](https://dask.pydata.org/en/latest/) cluster.


## Quick-start

The cluster can be deployed to the a local Docker installation with [`docker-compose`](https://docs.docker.com/compose/overview/) or a Docker Swarm with [`docker stack deploy`](https://docs.docker.com/engine/reference/commandline/stack_deploy/).

### Local Docker engine

To start the cluster:

```bash
docker-compose up -d
```

To destroy the cluster:

```bash
docker-compose rm -s -f
```

The cluster creates three services

- **scheduler**: Published on <http://localhost:8787>
- **worker**:
- **notebook**: Published on <http://localhost:8888>


### Docker Swarm

TODO
