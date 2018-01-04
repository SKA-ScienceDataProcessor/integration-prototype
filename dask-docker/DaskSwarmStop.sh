docker service rm worker
docker service rm scheduler
docker swarm leave --force
docker network rm sip
