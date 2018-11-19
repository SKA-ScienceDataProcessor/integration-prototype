#!/bin/bash
docker service rm worker
docker service rm scheduler
docker service rm sip_modeling
docker service rm sip_processing
docker network rm ical_dask
