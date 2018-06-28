docker stop processing
docker rm processing

# Run pipeline container with bound ARL and pipeline folders

docker run -d -it --name processing -v /home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/algorithm-reference-library:/home/sdp/algorithm-reference-library -v /var/run/docker.sock:/var/run/docker.sock -v /home/vlad/software.x32/SKA/integration-prototype/sip/science_pipeline_workflows/ical_dask/pipelines:/home/sdp/pipelines --entrypoint /home/sdp/pipelines/imaging-processing.py dask_pipeline

