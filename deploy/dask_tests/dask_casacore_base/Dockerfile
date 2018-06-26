FROM skasip/dask_worker_base

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:kernsuite/kern-4 && \
    apt-get update && \
    apt-get install -y python3-casacore
