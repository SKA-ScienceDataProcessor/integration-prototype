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

Run with:

```bash
docker stack deploy -c docker-compose.yml test
```

This will produce a set of output files in the `./output` directory consiting
of logs collected by the fluentd container.

To stop the containers and clean up:

```bash
docker stack rm test
rm -f output/docker.*
```

### Running on P3

This assumes running on the SIP shared Docker Swarm platform on P3
(<https://confluence.ska-sdp.org/display/WBS/Available+Shared+Platforms>).

#### Using `docker run`

```bash
docker run -d --log-driver=fluentd \
    --log-opt tag="{{.ImageName}}/{{.Name}}/{{.ID}}" \
    --name=log_test_1 skasip/log_spammer:latest 0.1
```

To stop and remove the logger

```bash
docker rm -f log_test_1
```

#### Using Docker Swarm:


```bash
docker stack deploy -c docker-compose.p3.hostnet.yml log_test
```

To stop and remove the stack

```bash
docker stack rm log_test
```


### Building and publishing the Docker image

```bash
docker build -t skasip/log_spammer:latest .
docker push skasip/log_spammer:latest
```
