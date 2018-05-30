# Test Container: `skasip/log_spammer`

## Introduction

This is an extremely simple container designed simply to spam log messages.

A Docker compose file is provided for testing deployment to Docker Swarm
with the logging driver configured to send logs to a fluentd container.
The fluentd container is configured (see `./fluentd/fluent.conf`) to write
any log messages it receives from the Docker logging source a set of files
which are bind mounted to the output directory.

## Quick-start

### Running locally

Build Docker `skasip/log_spammer` image with (this step can be skipped if using
the [hub.docker.com](https://hub.docker.com/r/skasip/log_spammer/) image):

```bash
docker-compose build
```

Run with:

```bash
docker stack deploy -c docker-compose.yml test
```

This will produce a set of output files in the `./output` directory consiting
of logs collected by the fluentd container.

To stop the containers and clean up:

```bash
docker stack rm test
rm -f output/*.*
```

### Running on P3

This assumes running on the SIP shared Docker Swarm platform on P3
(<https://confluence.ska-sdp.org/display/WBS/Available+Shared+Platforms>).

#### Running on the Swarm leader node:

```bash
docker run -d --log-driver=fluentd \
    --log-opt tag="{{.ImageName}}/{{.Name}}/{{.ID}}" \
    --name=log_test_1 skasip/log_spammer:latest
```

To stop and remove the logger

```bash
docker rm -f log_test_1
```

#### Using Docker Swarm:


```bash
docker stack deploy -c docker-compose.p3.yml log_test_2
```

To stop and remove the stack

```bash
docker stack rm log_test_2
```

