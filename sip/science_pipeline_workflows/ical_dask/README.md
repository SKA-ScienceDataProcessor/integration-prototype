# ICAL Dask Pipeline Workflow

## Description
This is a test ICAL pipeline based on the ARL example notebook
https://github.com/SKA-ScienceDataProcessor/algorithm-reference-library/blob/master/workflows/notebooks/imaging-pipelines.ipynb

It uses Dask parallel framework which is deployed as a Docker Swarm servcie. The pipeline itself also works inside
a Docker container.

## Downloading and installing ARL
A stable version of ARL is archived in a tarball together with it's data files. This tarball, which is kept in Cambridge Astrophysics'
ftp area, is downloaded by the install script *DockerBuild_bind.sh* and unpacked locally in *algorithm-reference-library* folder.
This folder is later bound to the docker containders as an external volume.

## Building Docker images
In the current version the images *dask_scheduler, dask_worker* and *dask_pipeline* are built locally using a shell script 
*DockerBuild_bind.sh* using the dockerfiles in *dockerfiles* folder.

## Starting Docker Swarm and the pipeline
The Docker Swarm Dask services and a pipeline container can be started by a shell script *dockerfiles/DaskSwarmStart_bind.sh* . 
Please note that the current version supports only locally deployed Docker Swarm (e.g. only one computer).

## Checking the pipeline execution and results
It is possible to monitor the pipeline execution via Dask Bokeh web interface which is exposed on http://0.0.0.0:8787
(http://localhost:8787 may not work due to the containerized Dask service). The results are saved into the
*algorithm-reference-library/test_results/* folder which is a persistent data storage for the pipeline.

## Troubleshooting
The ARL Dask interface requires an IP-address for a Dask scheduler to be set in the environment variable *ARL_DASK_SCHEDULER*
which is hardcoded in the dockerfile *dockerfiles/Dockerfile.pipeline_bind*. However, there is no garantee that on another computer
with different OS and Docker version it will be the same. If stdout of the pipeline container shows that it can't connect
to the Dask scheduler one has to check what actual IP address the Dask scheduler exposes. It can be checked in the 
stdout of the Dask scheduler container, where the first several lines whould be like that:

```
distributed.scheduler - INFO - -----------------------------------------------
distributed.scheduler - INFO - Clear task state
distributed.scheduler - INFO -   Scheduler at:     tcp://172.18.0.3:8786
distributed.scheduler - INFO -       bokeh at:                     :8787
distributed.scheduler - INFO - Local Directory:    /tmp/scheduler-zy4pgozd
distributed.scheduler - INFO - -----------------------------------------------
```
The IP address in the dockerfile *dockerfiles/Dockerfile.pipeline_bind* 
```
ENV ARL_DASK_SCHEDULER=172.18.0.3:8786
```
should be changed accordingly.

One can use UI For Docker to check stdout/stderr of the containers as well as to monitor Docker using web interface,
https://github.com/kevana/ui-for-docker .

## Stopping Dask Swarm
To remove services and stop network interface one can use a shell script *dockerfiles/DaskSwarmStop.sh* .

Note: It is recommended to stop Docker Swarm and wait a bit before restarting it again, otherwise the system
has not enough time to release the resources like the Dask scheduler IP-address and can assing another one.

## ToDo
1. Modeling and pipeline stages to be separated in two different scripts
2. Automatic Dask scheduler IP discovery by the pipeline cointainer
3. Starting pipeline container only when Dask service is started (timeouts?)



