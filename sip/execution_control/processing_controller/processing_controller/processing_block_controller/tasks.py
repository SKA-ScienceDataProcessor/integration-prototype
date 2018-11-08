# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task.

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import json
import logging
import os
import sys

import jinja2
from celery import Celery
from config_db.pb import ProcessingBlock
from docker_client import DockerClient

# import docker
# import docker.types

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
def execute_processing_block(pb_id: str):
    """Execute a processing block.

    Args:
        pb_id (str): The PB id for the PBC

    """
    log = logging.getLogger('sip.ec.pbc')

    log.info('**** Executing Processing block! ****')
    log.info('Starting workflow')
    print('XX', pb_id)

    pb = ProcessingBlock(pb_id)
    docker = DockerClient()

    workflow_stages = pb.workflow_stages
    running_service_ids = []

    while True:

        # Check dependencies and get list of stages ready to start.
        # ...
        # Check if the stage is complete
        # while True:
        #     for service_id in running_service_ids:
        #         if service is complete:
        #             del run_service_id[service_id]
        #
        #     break
        # # Check if complete
        stages = [workflow_stages[0]]

        # Start stages.
        for stage in stages:
            # Configure EE
            log.info('workflow stage: %s', stage.id)
            log.info('xxx %s', stage.args_template)
            args_template = jinja2.Template(stage.args_template)
            log.info('xxx3 %s', json.dumps(stage.config))
            args = args_template.render(stage=stage.config,
                                        **pb.workflow_parameters)
            args = json.dumps(json.loads(args))
            log.info('**********')
            log.info('ARGS: %s', args)

            compose_template = jinja2.Template(stage.compose_template)
            log.info('xxx1  %s', stage.compose_template)
            compose_str = compose_template.render(stage=dict(args=args))
            log.info('**********')
            log.info('COMPOSE_STR: {}'.format(compose_str))

            # Run the compose file
            docker.create_services(compose_str)
            # running_service_ids.append(serivce_id)
            # update db status

        # if there are not more stages -> break
        break

    # timeout = config.get('timeout', None)
    # start_time = time.time()
    # while True:
    #     time.sleep(0.5)
    #     log.debug('Executing workflow ... %.1f s', (time.time() - start_time))
    #     if timeout and time.time() - start_time > timeout:
    #         break




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
