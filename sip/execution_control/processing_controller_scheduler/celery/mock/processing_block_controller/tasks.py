# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import os
import logging
import time
import json

import docker
import docker.types

from celery import Celery

BROKER = os.getenv('CELERY_BROKER', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)
LOG = logging.getLogger('sip.processing_block_controller')
_HANDLER = logging.StreamHandler()
_HANDLER.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - '
                                        '%(name)s - '
                                        '%(levelname).1s - '
                                        '%(message)s',
                                        '%Y-%m-%d %H:%M:%S'))
LOG.setLevel(logging.DEBUG)
LOG.addHandler(_HANDLER)


@APP.task
def execute_processing_block(config):
    """Execute a processing block.

    Args:
        config (dict): Processing Block Configuration.
    """
    LOG.info('**** Executing Processing block! ****')
    LOG.info('config: %s', json.dumps(config))
    # print('Executing Processing Block, id = ', config['id'])
    # time.sleep(3.0)
    LOG.info('Starting workflow')
    client = docker.from_env()

    # Make sure we are on a manager node ...
    # manager = client.info()['Swarm']['ControlAvailable']
    # if not manager:
    #     LOG.critical()

    # images = client.images.list()
    # for image in images:
    #     LOG.debug(image)

    # Run the docker task
    # https://github.com/bmort/docker_tests/blob/master/volume_bind/launch_service.py
    service = client.services.create(
        image='skasip/mock_workflow_task_01:latest',
        name="mock_workflow_task_01",
        restart_policy=docker.types.RestartPolicy(condition='none'),
        mode=docker.types.ServiceMode(mode='replicated', replicas=1))

    LOG.info('Service ID: %s', service.id)


