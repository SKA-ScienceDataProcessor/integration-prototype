# Processing Controller Scheduler (Celery variant)

This is an extremely lightweight prototype of the Processing Controller
Scheduler which offloads the execution of Processing Blocks to Processing
Block Controllers implemented as a set of 
[Celery](http://www.celeryproject.org/) tasks.

For testing and stand-alone operation a number of mock components are provided.


## Quick-start


1. Build docker images
   
   ```bash
   docker build -t skasip/mock_pbc mock/processing_block_controller
   ```

1.  Start backing services

    ```bash
    docker stack deploy -c docker-compose.dev.yml pc
    ```
    
    This consists of:
    
    - a Redis database used for the Celery broker, Celery
      backend, and mock Execution Control Configuration database,
    - a Mock Processing Block Controller Service,
    - and a Redis Commander Web UI for viewing the contents of the 
      Configuration database.
    
    *Note: that the Redis service is not backed by a docker volume in this
     compose file as this is not needed during testing*

1.  Create a virtualenv for application dependencies:

    ```bash
    python3 -m venv venv    
    source venv/bin/activate
    pip install -r requirements.txt
    ```

1. Start the Scheduler application:

    ```bash
    python3 -m app
    ```

1.  Use the provided utilities for adding and removing Processing and Scheduling
    blocks from the mock Configuration database.

    ```bash
    python3 -m utils.create_scheduling_block
    python3 -m utils.delete_scheduling_block
    python3 -m utils.delete_processing_block
    ```

1.  Clean up:

    ```bash
    docker stack rm pc
    ```
    
## Debugging

* If you have started the development backing services a web UI to the 
  configuration database can be viewed at <http://localhost:8081>


## Unit tests

TODO(BM)
