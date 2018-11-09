# Tango Control package

For a description of this package see Section 7.6 of the SIP report.

## Start Docker containers

```bash
docker stack deploy -c docker-compose.yml tango
```

## Interactive use of Containers (useful in testing)

This container is started with its `/home/sip` folder bound to the 
code folder for which it is associated.

In order to start an interactive session inside the container use the
following command: 

```bash
docker exec -it <tagno_test_device container id> /bin/bash
```
