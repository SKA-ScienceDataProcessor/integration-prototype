# Docker (Swarm) Dask cluster deployment

## Quick-start

```bash
docker stack deploy -c docker-compose.yml dask
```

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r dask distributed
python3 quickstart01.py
```




































## old notes .....................

Extremely experimental
[Docker Compose file](https://docs.docker.com/compose/compose-file/)
to deploy a test [Dask](https://dask.pydata.org/en/latest/) cluster.

Based on: <https://github.com/dask/dask-docker>

## Quick-start

The cluster can be deployed to the a local Docker installation with
[`docker-compose`](https://docs.docker.com/compose/overview/) or a
Docker Swarm with [`docker stack deploy`](https://docs.docker.com/engine/reference/commandline/stack_deploy/).

### Local Docker engine

To start the cluster:

```bash
docker-compose up -d
```

To destroy the cluster:

```bash
docker-compose rm -s -f
```

The cluster creates three services:

- **scheduler**: The Dask scheduler daemon, published on
  <http://localhost:8787>
- **worker**: A Dask worker.
- **notebook**: A Jupyter notebook that can be used for interacting with the
  Dask Cluster. Published on <http://localhost:8888>. In order to use this
  an access token is required. This is found in the log of the notebook
  container which can be viewed with `docker logs dask_cluster_notebook_1`.

### Docker Swarm

To deploy to Docker Swarm:

```bash
docker stack deploy -c docker-compose.yml dask
```

To remove the stack:

```bash
docker stack rm dask
```

In order to run a very simple test script using this cluster:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r dask distributed
python3 quickstart01.py
```
