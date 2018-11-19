#!/bin/bash
docker stack deploy --compose-file docker-compose.start_ee.yml dask-stack --prune
docker stack deploy --compose-file docker-compose.process_data.yml processing-stack --prune
