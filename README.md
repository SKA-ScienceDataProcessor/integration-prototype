[![Documentation Status](https://readthedocs.org/projects/integration-prototype/badge/?version=latest)](http://integration-prototype.readthedocs.io/en/latest/?badge=latest)
[![Build Status](http://128.232.224.174/buildStatus/icon?job=sip/master)](http://128.232.224.174/job/sip/job/master/)
[![GitHub (pre-)release](https://img.shields.io/github/release/SKA-ScienceDataProcessor/integration-prototype/all.svg)](https://github.com/SKA-ScienceDataProcessor/integration-prototype/releases)

# SDP Integration Prototype

This is an experimental Docker Swarm version with Dask/Distributed. 
It is configured for a single node computer.

Apache Spark is not tested on this branch

## Requirements
* Docker
* Python 3.4 or later
* DockerPy 2.1 or later
* rpyc
* zmq
* pyftpdlib
* Apache Spark (for spark-submit)
* Dask
* Distributed

## Docker images build
Run DockerBuild.sh from $SIPROOT which creates three docker images,
* sip
* dask_scheduler
* dask_worker

Attention: it takes a while.

## Docker Swarm start with Dask Scheduler/Worker containers
Run dask-docker/DaskSwarmStart.sh, it starts scheduler and worker Swarm services
Point your browser to http://0.0.0.0:8787/status to check Dask status.
The script attaches automatically to the worker container for testing/debugging purposes.

## Start SIP master
Execute "jupyter notebook" from $SIPROOT and run sip-master.ipynb notebook.
The terminal with log output will be launched (requires gnome-terminal installed).
Type "online" in the prompt field in the end of the notebook, the task ical-pipeline.py
(defined in etc/slave_map.json) will be launched in "sip" container using containerized dask scheduler and worker. 
Check Dask status on the webpage. When it completes, type "offline" and "shutdown".

## Stop Docker Swarm
Run dask-docker/DaskSwarmStop.sh
