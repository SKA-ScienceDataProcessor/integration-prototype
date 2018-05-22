# Test Container: Log Spammer 

This is an extremely simple container designed simply to spam log messages

## Quickstart

Build Docker `skasip/log_spammer` image with (this step can be skipped if using 
the [hub.docker.com](https://hub.docker.com/r/skasip/log_spammer/) image): 

```bash
docker-compose build
```

Run the Container using:

```bash
docker-compose up
``` 

Destroy (remove and stop) the container using

```bash
docker-compose rm -s -f
```

### Logging Drivers

Compose files for testing with the `json` and `fluentd` 
[logging drivers](https://docs.docker.com/config/containers/logging/configure/) 
are also provided.

The `json` logging driver is provided for simple testing demonstrating 
how a docker logging driver can be configured, and the
`fluentd` logging driver is provided for testing with the Monasca logging
solution on P3 when using the `fluentd` container deployed as a logging 
sidecar container on the Swarm Cluster.

To use either of these options select the relevant compose file using the 
`-f` flag with `docker-compose`.

 
