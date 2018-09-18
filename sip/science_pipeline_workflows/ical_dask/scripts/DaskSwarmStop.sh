#!/bin/bash
docker service rm worker
docker service rm scheduler
docker network rm ical_dask
