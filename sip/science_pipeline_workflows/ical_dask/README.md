# ICAL Dask Pipeline Workflow

## Description

This is a test ICAL pipeline based on the ARL example notebook
<https://github.com/SKA-ScienceDataProcessor/algorithm-reference-library/blob/master/workflows/notebooks/imaging-pipelines.ipynb>

It uses Dask parallel framework which is deployed as a Docker Swarm service.
The pipeline itself also works inside a Docker container.

## Downloading and installing ARL

A stable version of ARL is archived in a tarball together with it's data files.
This tarball, which is kept in Cambridge Astrophysics' ftp area, is downloaded
by the install script `DockerBuild_bind.sh` and unpacked locally in
`pipelines/sdp_arl` folder. This folder is later bound to the docker
containers as an external volume.

## Building Docker images

The images `ical_dask_scheduler`, `ical_dask_worker` and `ical_dask_pipeline` 
are built using the shell script `DockerBuild_bind.sh` and the Dockerfiles 
in `dockerfiles` folder.

## Starting Docker Swarm

The Docker Swarm Dask services can be started in two different ways: using
`docker stack deploy` or with a provided shell script.

*Please note that the current version supports only locally deployed Docker
Swarm (e.g. only one computer).*

### Docker stack deploy

To start the Dask scheduler and worker(s) service containers.

First create a overlay network with:

```bash
docker network create --driver overlay --attachable ical_sip 
```

Then start the ICAL Dask Execution Engine service stack with:

```bash
docker stack deploy -c scripts/docker-compose.start_ee.yml ical_dask
```

### Shell script

The Docker Swarm Dask services can be started by a shell script
`scripts/DaskSwarmStart_bind.sh`. The script will start Swarm services for a
dask scheduler and a dask worker.


## Starting ICAL pipeline

There are three shell scripts that start an ICAL pipeline container with three
different workflow scripts:

* *scripts/DaskSwarmModeling.sh* starts a container with
  `pipelines/imaging-modeling.py` which creates a visibility list
  for some particular configuration *(LOWBD2, nfreqwin=7, ntimes=11,
  rmax=300.0, phasecentre=(+30.0deg, -60.0deg))* as well as simulates the
  visibilities for some sources from GLEAM catalogue. It also exports the
  modeled data in HDF5 files, and stores parameters into pickle objects and
  numpy-formatted files.

* `scripts/DaskSwarmProcessing.sh` starts a container with
  `pipelines/imaging-processing.py` which reads all saved files and
  performs data processing using `deconvolve_component()`,
  `continuum_imaging_component()` and ical_component() functions from ARL

## Checking the pipeline execution and results

It is possible to monitor the pipeline execution via Dask Bokeh web
interface which is exposed on <http://0.0.0.0:8787> (<http://localhost:8787>
may not work due to the containerized Dask service). The results including
intermediate HDF5 files are saved into the
`algorithm-reference-library/test_results/` folder which is a persistent data
storage for the pipeline.

## Troubleshooting

The ARL Dask interface requires an IP-address for a Dask scheduler to be set
in the environment variable `ARL_DASK_SCHEDULER` which is hardcoded in the
dockerfile `dockerfiles/Dockerfile.pipeline_bind`. However, there is no
guarantee that on another computer with different OS and Docker version
it will be the same. If stdout of the pipeline container shows that it
can't connect to the Dask scheduler one has to check what actual IP address
the Dask scheduler exposes. It can be checked in the stdout of the Dask
scheduler container, where the first several lines would be like that:

```bash
distributed.scheduler - INFO - -----------------------------------------------
distributed.scheduler - INFO - Clear task state
distributed.scheduler - INFO -   Scheduler at:     tcp://172.18.0.3:8786
distributed.scheduler - INFO -       bokeh at:                     :8787
distributed.scheduler - INFO - Local Directory:    /tmp/scheduler-zy4pgozd
distributed.scheduler - INFO - -----------------------------------------------
```

The IP address in the dockerfile `dockerfiles/Dockerfile.pipeline_bind`

```Dockerfile
ENV ARL_DASK_SCHEDULER=172.18.0.3:8786
```

should be changed accordingly.

One can use UI For Docker to check stdout/stderr of the containers as well as
to monitor Docker using web interface,

<https://github.com/kevana/ui-for-docker> .

## Stopping Dask Swarm

To remove services and stop network interface one can use a shell script
`scripts/DaskSwarmStop.sh`.

Note: It is recommended to stop Docker Swarm and wait a bit before restarting
it again, otherwise the system has not enough time to release the resources
like the Dask scheduler IP-address and can assign another one.

## Todo

1. Automatic Dask scheduler IP discovery by the pipeline container
