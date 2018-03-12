cp sip/common/docker_paas_bind.py sip/common/docker_paas.py
wget -c -t 10 http://www.mrao.cam.ac.uk/projects/ska/arl/algorithm-reference-library.tar.gz
tar xvzf algorithm-reference-library.tar.gz && rm -f algorithm-reference-library.tar.gz
mkdir -p results
docker build -f Dockerfile.ARL_bind . -t sip
docker build -f dask-docker/Dockerfile.scheduler . -t dask_scheduler
docker build -f dask-docker/Dockerfile.worker_bind . -t dask_worker
docker volume create arl-results
