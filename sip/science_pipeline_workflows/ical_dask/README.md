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

## Starting Docker Swarm
The Docker Swarm Dask services can be started by a shell script *scripts/DaskSwarmStart_bind.sh* . 
The script will start Swarm services for a dask scheduler and a dask worker.
Please note that the current version supports only locally deployed Docker Swarm (e.g. only one computer).
Also it is required to replace all hard-coded path strings, e.g. "/home/vlad/software.x32/SKA/" with the actual ones.

## Starting ICAL pipeline
There are three shell scripts that start ICAL pipeline container with three different entrypoints (which are just python scripts).
* A script *scripts/DaskSwarmModeling.sh* starts a container with *pipelines/imaging-modeling.py* entrypoint which creates a visibility list for some particular configuration 
(LOWBD2, nfreqwin=7, ntimes=11, rmax=300.0, phasecentre=(+30.0deg, -60.0deg) ) as well as simulates the visibilities for some sources from GLEAM catalogue.
It also exports the modeled data in HDF5 files, and stores parameters into pickle objects and numpy-formatted files.
* A script *scripts/DaskSwarmProcessing.sh* starts a container with *pipelines/imaging-processing.py* entrypoint which reads all saved files and performs data processing using deconvolve_component(), continuum_imaging_component() and ical_component() functions
from ARL
* A script *scripts/DaskSwarmICALstart.sh* starts a container with *pipelines/ical-pipeline.py* entrypoint which performs both modelling and data processing internally.
Again, it is required to replace all hard-coded path strings, e.g. "/home/vlad/software.x32/SKA/" with the actual ones.

## Checking the pipeline execution and results
It is possible to monitor the pipeline execution via Dask Bokeh web interface which is exposed on http://0.0.0.0:8787
(http://localhost:8787 may not work due to the containerized Dask service). The results including intermediate HDF5 files are saved into the
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

### An example how to fix the wrong IP address

1. Run DockerUI container (https://github.com/kevana/ui-for-docker), 
```
docker run -d -p 9000:9000 --privileged -v /var/run/docker.sock:/var/run/docker.sock uifd/ui-for-docker
```

2. Open your browser to http://localhost:9000 , check that DockerUI works.

3. Start Dask Swarm services with
*scripts/DaskSwarmStart_bind.sh*

4. Refresh DockerUI in your browser, check that a scheduler container is running, it should be named something like 
```
scheduler.1.6ahfnu8tzehk7by4jy4izevn0
```

5. Go to http://localhost:9000/#/containers/

6. Click on stdout/stderr link for the scheduler container

7. Check the string with IP address in the top of stdout, e.g.
```
distributed.scheduler - INFO -   Scheduler at:     tcp://172.18.0.3:8786
```

8. Check if the same IP is exported in *dockerfiles/Dockerfile.pipeline_bind* and in *dockerfiles/Dockerfile.worker_bind* in a string
```
ENV ARL_DASK_SCHEDULER=172.18.0.3:8786
```
Replace with the actual one if necessary.

9. Re-build the images with DockerBuild_bind.sh (it will take little time since everything is cached).

10. Start pipeline/modeling processing containers.

## Stopping Dask Swarm
To remove services and stop network interface one can use a shell script *scripts/DaskSwarmStop.sh* .

Note: It is recommended to stop Docker Swarm and wait a bit before restarting it again, otherwise the system
has not enough time to release the resources like the Dask scheduler IP-address and can assing another one.

## ToDo
1. Automatic Dask scheduler IP discovery by the pipeline cointainer


