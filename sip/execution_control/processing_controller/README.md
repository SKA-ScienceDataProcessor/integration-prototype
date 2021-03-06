# Processing Controller Scheduler (Celery variant)

This is an extremely lightweight prototype of the Processing Controller
Scheduler which offloads the execution of Processing Blocks to Processing
Block Controllers implemented as a set of 
[Celery](http://www.celeryproject.org/) tasks.

For testing and stand-alone operation, a number of mock components are 
provided.


## Quick-start


1. (optional) Build the Processing Block Controller Docker image
   
   ```bash
   docker build -t skasip/pbc processing_block_controller
   ```

1.  Start backing services

    ```bash
    docker stack deploy -c docker-compose.dev.yml pc
    ```
    
    This consists of:
    
    - a Redis database used for the Celery broker, Celery
      backend, and mock Execution Control Configuration database,
    - the Processing Block Controller Service,
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
    python3 -m scheduler
    ```

1.  Use the provided utilities for adding and removing Processing and Scheduling
    blocks from the mock Configuration database.

    ```bash
    python3 -m processing_controller.scripts.skasip_pc_add_sbi
    ```

1.  Clean up:

    ```bash
    docker stack rm pc
    ```
    
## Debugging

* If you have started the development backing services a web UI to the 
  configuration database can be viewed at <http://localhost:8081>


## Unit tests

```bash
pytest -s -v --codestyle --docstyle --pylint tests/
```
