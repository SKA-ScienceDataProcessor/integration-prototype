# Example SIP Dask worker base image

This is a copy of the Dask base image with the entrypoint specialised
to running a Dask worker process. It is intended to be a base image for
extending for other Dask workers.

## Build instructions

```bash
docker build -t skasip/dask_worker_base .
```
