# SIP Portainer Deployment

This Docker Compose file launches Portainer on top of Docker Swarm.

Portainer is very helpful to manage containers and volumes on P3-ALaSKA, and
inspect their outputs. If the services are not already running, they can be
launched from this directory by running:

```bash
docker stack deploy -c docker-compose.yml portainer
```

Once the service is running, go to the Swarm master at
<http://10.60.253.14:9000>

Ask on the SIP Slack channel if you need the login details.

See <https://portainer.io/>
