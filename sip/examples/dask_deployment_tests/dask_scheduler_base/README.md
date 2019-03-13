# Example SIP Dask scheduler base image

This is a Dask base image with Bokeh installed and the entrypoint specialised
to running a Dask Scheduler process. It is intended to serve as a base image
for more specialised Dask Schedulers.

## Build instructions

```bash
docker build -t skasip/dask_scheduler_base .
```
