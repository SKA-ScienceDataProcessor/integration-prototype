# SIP Visibility ingest workflow

## Introduction

This workflow script uses a combination of SPEAD asyncio and blocking worker
threads to asynchronously receive and perform ingest processing on visibility
data streamed from CSP.

This workflow assumes that each ingest processes receives and processes the 
complete time stream for a set of channels (which may be as many as ~300).

The total data from CSP for the scheduling block, which may consist of as much
as ~65k channels, is then split between a number of ingest processes.

The assumption we are taking is that these ingest processes can be deployed 
as a set of Docker containers using container orchestration (currently 
Docker Swarm).

The main workflow function is in the `recv` folder and a a CSP emulator is 
provided in the `send` folder.

Docker images for the current version of send and receive can be found in
[hub.docker.com](https://hub.docker.com/u/skasip) and have the names:

- `skasip/csp_vis_sender` for the CSP emulator and,
- `skasip/ingest_visibilities` for the ingest workflow.

For additional details see the `README.md` files in the `send` and `recv` 
folders. 


## Quick-start

### Single sender and receiver (without Docker)

1\. Create a virtualenv:

```bash
virtualenv -p python3 venv
```

2\. activate and install dependencies:

```bash
source venv/bin/activate
pip intstall -r send/requirements.txt
pip intstall -r recv/requirements.txt
```

3\. Run the receiver:

```bash
python3 send/async_recv "$(< recv/spead_recv.json)"
```

4\. Run the sender:


```bash
python3 send/async_send "$(< send/spead_send.json)"
```

### Single sender and receiver on a local Docker engine

1\. Build the docker images:

```bash
docker build -t skasip/spead_base ./spead_base
docker build -t vis_send ./send
docker build -t vis_recv ./recv
```

2\. Run the receiver:

```bash
docker run --rm --name=recv1 --restart=no --network=host vis_recv "$(< recv/spead_recv.json)"
```

3\. Run the sender:

```bash
docker run --rm --name=send1 --restart=no --network=host vis_send "$(< send/spead_send.json)"
```

### Single sender and receiver using Docker Swarm (local install)

1\. Run the receiver:

```bash
docker service create -d --name=recv1 --restart-condition=none \
    --stop-signal=INT --network=host vis_recv "$(< recv/spead_recv.json)"
```

2\. Run the sender:

```bash
docker service create -d --name=send1 --restart-condition=none \
    --stop-signal=INT --network=host vis_send "$(< send/spead_send.json)"
```

3\. Check the logs:

```bash
docker service logs recv1
docker service logs send1
```

4\. Remove the services:

```bash
docker service rm send1
docker service rm recv1
```

### Single sender and receiver using Docker Swarm (P3)


1\. Run the receiver:

```bash
docker service create -d --name=recv1 --restart-condition=none \
    --log-driver=fluentd --log-opt tag="{{.ImageName}}/{{.Name}}/{{.ID}}" \
    --constraint='node.labels.recv == 01' \
    --stop-signal=INT --network=host skasip/ingest_visibilities \
    "$(< recv/spead_recv.json)"
```

2\. Run the sender:

```bash
docker service create -d --name=send1 --restart-condition=none \
    --log-driver=fluentd --log-opt tag="{{.ImageName}}/{{.Name}}/{{.ID}}" \
    --constraint='node.labels.send == 01' \
    --stop-signal=INT --network=host skasip/csp_vis_sender \
    "$(< send/spead_send.json)"
```

3\. Remove the services:

```bash
docker service rm send1
docker service rm recv1
```


### Multiple senders and receivers using Docker Swarm

TODO

## Adding / updating images [hub.docker.com](https://hub.docker.com/u/skasip)

```bash
docker tag vis_send skasip/csp_vis_sender
docker push skasip/csp_vis_sender
docker tag vis_recv skasip/ingest_visibilities
docker push skasip/ingest_visibilities
```

## Labeling nodes on Docker Swarm

Nodes can be labeled with:

```bash
docker node update --label-add key=value <node id>
```

Node labels can be inspected with:

```bash
docker node inspect <node id>
```

Node labels can be removed with:

```bash
docker node update --label-rm key <node id>
```

In the current SIP shared swarm cluster on P3:

- node 0, id=ssx7te87j0fbx1ufzihz5vti6, is labeled with `send=01` and,
- node 1, id=y2mgesm65oqmjhrn4ejwg9k5v, is labeled with `recv=01`.

The BDN IPs are:
- node 0 is `10.11.0.11`
- node 1 is `10.11.0.4`





 
