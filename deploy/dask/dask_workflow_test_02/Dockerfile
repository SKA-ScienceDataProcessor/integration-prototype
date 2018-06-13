FROM skasip/dask_worker_base

RUN pip3 install astropy

WORKDIR /app

# May not be needed?
# https://stackoverflow.com/questions/41475239/how-to-set-up-logging-on-dask-distributed-workers
# COPY config.yaml /app/config.yaml
# ENV DASK_CONFIG /app/config.yaml

COPY workflow /app/workflow
ENV PYTHONPATH ${PYTHONPATH}:/app
