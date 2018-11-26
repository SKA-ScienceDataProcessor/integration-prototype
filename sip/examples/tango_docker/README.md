# SIP Tango Docker experiment

## Notes

The following set up allows a containerised TangoDevice

- TangoDB (mysql) started with the `tango-controls/docker-mysql` image
- Tango DataBaseds (plus a number of other tango services) is started in 
  another container using the `tango-controls/tango-cs-docker` image. 
- A third image based on the docker `ubuntu:17.04` image is defined in the
  `Dockerfile` in this directory which could contain Tango device service 
  application code. At the moment it just installs tango and an ipython3
  environment so that interactive testing can be done. (eg. 
  <http://pytango.readthedocs.io/en/latest/quicktour.html>)

## Quickstart

To build the `skasip/pytango-example` image (skip this to use the version on 
[DockerHub](https://cloud.docker.com/swarm/skasip/repository/registry-1.docker.io/skasip/pytango-example/general)).

```bash
docker-compose build
```
To start the containers:

```bash
docker-compose up -d
```

Get a bash prompt inside the pytango-example container:

``` bash
docker exec -it tagnodocker_pytango-example_1 /bin/bash
```

Inside this container, you should be able to use ipython3, import tango and 
run tango commands as this container is preconfigured to talk to the Tango 
DataBaseds server running in the `tango-cs` container.

Once finished, clean up with:

```bash
docker-compose rm -s -f
```

## References

- <http://pytango.readthedocs.io/en/latest/>
- <http://tango-controls.readthedocs.io/en/latest/development/debugging-and-testing/testing-tango-using-docker.html?highlight=docker>
- <https://github.com/tango-controls/docker-mysql>
- <https://github.com/tango-controls/tango-cs-docker>
