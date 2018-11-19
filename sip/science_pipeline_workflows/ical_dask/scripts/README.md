## Using docker stack deploy

To use yml docker-compose files one has to set dask_stack name for a Dask stack,

```
docker stack deploy --compose-file docker-compose.start_ee.yml dask-stack --prune
docker service logs dask-stack_worker --follow
docker service logs dask-stack_scheduler --follow
docker stack remove dask-stack
```

Other stacks can have any other names, e.g.

```
docker stack deploy --compose-file docker-compose.generate_data.yml modelling-stack --prune
docker stack deploy --compose-file docker-compose.process_data.yml processing-stack --prune
```

