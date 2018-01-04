docker service rm worker
docker service rm scheduler
docker swarm leave --force
docker network rm sip
docker swarm init
docker network create --driver overlay sip
docker service create --network sip --name scheduler --publish 8786:8786 --publish 8787:8787 dask_scheduler
docker service create --network sip --publish 8888:8888 --mode replicated --name worker dask_worker scheduler:8786 --nprocs 8 --nthreads 1
sleep 5
docker exec -it $(docker ps | grep worker | awk '{print  $1 " bash"}' )

