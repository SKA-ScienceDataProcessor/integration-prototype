#

## Quick-start

Build Images:

```bash
docker build -t skasip/dask_base dask_base
docker build -t skasip/dask_scheduler_base dask_scheduler_base
docker build -t skasip/dask_worker_base dask_worker_base
```

Run the scheduler and a single worker

```bash
docker run --name=sched --rm -d -p 8786:8786 -p 8787:8787 skasip/dask_scheduler_base
docker run --name=work1 --rm -d --link=sched skasip/dask_worker_base sched:8786
```

## Dask worker with python-casacore

(can be used with the scheduler above)

```bash
docker build -t skasip/dask_casacore_base dask_casacore_base
```

```bash
docker run --name=work3 --rm -d --link=sched skasip/dask_casacore sched:8786
```