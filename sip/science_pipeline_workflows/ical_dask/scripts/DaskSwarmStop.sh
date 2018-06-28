docker service rm worker
docker service rm scheduler
#docker service rm pipeline
docker stop pipeline
docker rm pipeline
docker swarm leave --force
docker network rm sip
