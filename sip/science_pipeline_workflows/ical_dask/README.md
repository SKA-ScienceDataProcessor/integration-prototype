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

## Starting Dask Execution Engine services

The Docker Swarm Dask Execution Engine services can be started in two different
ways: using `docker stack deploy`, or with a provided shell script. These
are described below.

### Using `docker stack deploy`

To start the Dask scheduler and worker(s) service containers.

First create a overlay network with:

```bash
docker network create --driver overlay --attachable ical_sip 
```

Then start the ICAL Dask Execution Engine service stack with:

```bash
docker stack deploy -c scripts/docker-compose.start_ee.yml ical_dask
```

### Using the provided shell (bash) script

The Docker Swarm Dask services can be started by the shell script
`DaskSwarmStart_bind.sh` found in the `scripts` directory. This script will 
start a custom overlay network called `ical_sip` and Docker Swarm services for 
a dask scheduler and a dask worker. The script can be run with the following 
command:

```bash
bash ./scripts/DaskSwarmStart_bind.sh
```


## Generating test input data

Before running the pipeline, it is necessary to generate some data for it to
process. Similarly to starting the Dask services (described in the previous
section), this can be done in two ways. Data is written to the `results`
folder which is exposed into the containers using a bind mount.


### Using `docker stack deploy`

The following command will create a service consisting of a single container
associated with the stack name `gen_data` 

```bash
docker stack deploy -c scripts/docker-compose.generate_data.yml gen_data
```

### Using the provided shell (bash) script

The following command will run a single container which will generate the test
data.

```bash
bash ./scripts/DaskSwarmModeling.sh
```

## Running the ICAL processing pipeline

Once the input data has been generated, it is now possible to run the 
ICAL pipeline. Again, this can be done in two ways.

### Using `docker stack deploy`

The following command will create a service consisting of a single container
associated with the stack name `run_ical` 

```bash
docker stack deploy -c scripts/docker-compose.process_data.yml run_ical
```

### Using the provided shell (bash) script

The following command will run a single container which will generate the test
data.

```bash
bash ./scripts/DaskSwarmProcessing.sh
```

## Checking the pipeline execution and results

It is possible to monitor the pipeline execution via Dask Bokeh web
interface which is exposed on <http://localhost:8787>. The results including
intermediate HDF5 files are saved into the `results` folder which is a 
persistent data storage for the pipeline.

## Stopping Dask Swarm

To remove services and stop network interface one can use a shell script
`scripts/DaskSwarmStop.sh`.

Note: It is recommended to stop Docker Swarm and wait a bit before restarting
it again, otherwise the system has not enough time to release the resources
like the Dask scheduler IP-address and can assign another one.

## Todo

1. Automatic Dask scheduler IP discovery by the pipeline container
