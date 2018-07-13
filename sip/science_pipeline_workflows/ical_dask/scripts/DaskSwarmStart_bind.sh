# Remove services if exist
docker service rm worker
docker service rm scheduler
#docker service rm pipeline

# Stop pipeline container and remove it
#docker stop pipeline
#docker rm pipeline

# Stop Swarm
docker swarm leave --force

# Remove network overlay
docker network rm sip

# Initialize default swarm
docker swarm init

# Create network overlay
docker network create --driver overlay sip

# Create Dask scheduler service and expose ports
docker service create --network sip --name scheduler --publish 8786:8786 --publish 8787:8787 dask_scheduler

# Create Dask worker service, bind ARL and expose jupyter notebook port (for debugging)
docker service create --network sip --publish 8888:8888 --mode replicated --mount type=bind,source=/home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/algorithm-reference-library,destination=/home/sdp/algorithm-reference-library --name worker dask_worker scheduler:8786 --nprocs 8 --nthreads 1

# Give enough time for Doask to start
#sleep 20

# Run pipeline container with bound ARL and pipeline folders
#docker run -d -it --name pipeline -v /home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/algorithm-reference-library:/home/sdp/algorithm-reference-library -v /var/run/docker.sock:/var/run/docker.sock -v /home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/pipelines:/home/sdp/pipelines dask_pipeline

#docker service create --network sip --mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock --mount type=bind,source=/home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/algorithm-reference-library,destination=/home/sdp/algorithm-reference-library --name pipeline  dask_pipeline
#sleep 10
#docker exec -it $(docker ps | grep pipeline | awk '{print  $1 " bash"}' )

