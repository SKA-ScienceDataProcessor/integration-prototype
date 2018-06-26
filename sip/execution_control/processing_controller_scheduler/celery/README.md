# Processing Controller Scheduler (Celery variant)

This is an extremely lightweight prototype of a Processing Controller
Scheduler which offloads the execution of Processing Blocks to Processing
Block Controllers implemented as a set of
[Celery](http://www.celeryproject.org/) tasks.

For testing and stand-alone operation a number of mock components are provided.

## Quick-start

Start a containerised Redis instance used for the Celery broker, Celery
backend, and mock Configuration database.

```bash
docker-compose -f docker-compose.dev.yml up -d
```

*Note: that the Redis service is not backed by a docker volume in this
compose file as this is not needed during testing*

Create a virtualenv for application dependencies:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the Scheduler application:

```bash
python3 -m app
```

Use the provided utilities for adding and removing Processing and Scheduling
blocks from the mock Configuration database.

```bash
python3 -m utils.create_scheduling_block
python3 -m utils.delete_scheduling_block
python3 -m utils.delete_processing_block
```

Clean up:

```bash
docker-compose -f docker-compose.dev.yml rm -s -f
```

## Unit tests

Run with:

```bash
pytest -m tests/test_queue.py
pytest -m test/test_celery_task.py
```
