# Tango Control package

For a description of this package see Section 7.6 of the SIP report.

## Start Docker containers

```bash
docker stack deploy -c docker-compose.yml tango
```

## Interactive use of the `tango_test_device`

This container is started with its `/app` folder bound to the 
code in `tango_test_device`, so changes in the code get updated in the 
container. This can be useful for development.

```bash
docker exec -it <tagno_test_device container id> /bin/bash
```
