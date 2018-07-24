wget -c -t 10 http://www.mrao.cam.ac.uk/projects/ska/arl/algorithm-reference-library.sip.20180605.tar.gz
tar xvzf algorithm-reference-library.sip.20180605.tar.gz && rm -f algorithm-reference-library.sip.20180605.tar.gz
mkdir -p results
docker build -f dockerfiles/Dockerfile.pipeline_bind . -t dask_pipeline
docker build -f dockerfiles/Dockerfile.scheduler . -t dask_scheduler
docker build -f dockerfiles/Dockerfile.worker_bind . -t dask_worker
#docker volume create arl-results
