docker build -f Dockerfile.ARL . -t sip
docker build -f dask-docker/Dockerfile.scheduler . -t dask_scheduler
docker build -f dask-docker/Dockerfile.worker . -t dask_worker

