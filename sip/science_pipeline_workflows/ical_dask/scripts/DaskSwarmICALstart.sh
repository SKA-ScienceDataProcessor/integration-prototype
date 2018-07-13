docker stop pipeline
docker rm pipeline

# Run pipeline container with bound ARL and pipeline folders
docker run -d -it --name pipeline -v /home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/algorithm-reference-library:/home/sdp/algorithm-reference-library -v /var/run/docker.sock:/var/run/docker.sock -v /home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/pipelines:/home/sdp/pipelines dask_pipeline

