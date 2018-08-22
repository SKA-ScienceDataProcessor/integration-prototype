# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task.

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import os
import sys
import logging
import time
import json

# import docker
# import docker.types

from celery import Celery

BROKER = os.getenv('CELERY_BROKER', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)


def init_logger():
    """Initialise the logger."""
    log = logging.getLogger('sip')
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = os.getenv('SIP_LOG_FORMAT', '%(asctime)s.%(msecs)03d | '
                    '%(name)s | %(levelname)-7s | %(message)s')
    handler.setFormatter(logging.Formatter(fmt, '%Y-%m-%d %H:%M:%S'))
    log.addHandler(handler)
    log.setLevel(os.getenv('SIP_PBC_LOG_LEVEL', 'INFO'))


init_logger()


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'execute_processing_block')
def execute_processing_block(config: dict):
    """Execute a processing block.

    Args:
        config (dict): Processing Block Configuration.
    """
    log = logging.getLogger('sip.ec.pbc')

    log.info('**** Executing Processing block! ****')
    log.info('config: %s', json.dumps(config))
    log.info('Starting workflow')
    timeout = config.get('timeout', None)
    start_time = time.time()
    while True:
        time.sleep(0.5)
        log.debug('Executing workflow ... %.1f s', (time.time() - start_time))
        if timeout and time.time() - start_time > timeout:
            break
    # The workflow configuration should contain the workflow template
    # and the configuration for each workflow stage.

    # Workflow stages are expected to be run as one or more Docker containers.
    # using an API to the container orchestration.

    # client = docker.from_env()
    # Make sure we are on a manager node ...
    # manager = client.info()['Swarm']['ControlAvailable']
    # if not manager:
    #     log.critical()
    # images = client.images.list()
    # for image in images:
    #     log.debug(image)
    # Run the docker task
    # https://github.com/bmort/docker_tests/blob/master/volume_bind/launch_service.py
    # service = client.services.create(
    #     image='skasip/mock_workflow_task_01:latest',
    #     name="mock_workflow_task_01",
    #     restart_policy=docker.types.RestartPolicy(condition='none'),
    #     mode=docker.types.ServiceMode(mode='replicated', replicas=1))
    # log.info('Service ID: %s', service.id)
