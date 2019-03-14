# Very Simple example workflow deployment using Docker

Very simple workflow deployed using the SIP Dask base Docker images
(ie. images with no dependencies other than Dask + Distributed).

## Quick-start

To deploy the dask cluster (1 scheduler + 1 worker).

```bash
docker stack deploy -c docker-compose.yml dask
```

Run the workflow script using the cluster:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r dask distributed
python3 quickstart01.py
```

Clean up:

```bash
docker stack rm dask
```
