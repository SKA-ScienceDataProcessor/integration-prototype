# Experiments with deploying containerised Dask using Docker Swarm

This folder contains a number of experiments used to assess and demonstrate
how Dask can be deployed using Docker Swarm.

This consists of a number of lightweight base images (`dask_base`,
`dask_worker_base`, and `dask_scheduler_base`) which extend the official
`ubuntu:18.04` base image with Dask packages to provide a generic Dask
Scheduler and Worker image that can either be used directly or extended by
other Dask workflows (depending if additional dependencies are required).

Use of these images are then explored in `dask_workflow_test_01` and
`dask_workflow_test_02`. These provide two examples of Deploying and
running a Dask workflow using Docker Swarm.
