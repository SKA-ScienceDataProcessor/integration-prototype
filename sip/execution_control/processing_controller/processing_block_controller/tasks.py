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
from copy import deepcopy
import time

import jinja2
from celery import Celery
from sip_config_db.scheduling import ProcessingBlock
from sip_docker_swarm import DockerClient, __version__
from sip_logging import init_logger


# import docker
# import docker.types

BROKER = os.getenv('CELERY_BROKER', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)


init_logger(log_level='DEBUG')


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'execute_processing_block_2')
def execute_processing_block_2(pb_id: str):
    """Execute a processing block.

    {
        "status": "none(change to: unknown?)" -> "running" -> "complete" ("aborted", "failed")
        "services": {
            'id': {
                "name": ".."
                "status": ".."
                "complete": True|False
            },
            {
                "service_id": "..",
                "status": ".."
            },


        },
        ...
    }

    Args:
        pb_id (str): The PB id for the PBC

    """
    log = logging.getLogger('sip')
    log.propagate = False  # FIXME(BMo) Make propagate a option on
                           # init_logger (default = False)?

    log = logging.getLogger('sip.ec.pbc')

    log.info('Using docker swarm api version: %s', __version__)
    log.info('**** Executing Processing block: %s! ****', pb_id)
    log.info('Starting workflow ... ')

    pb = ProcessingBlock(pb_id)
    docker = DockerClient()

    stage_dict = {}
    for stage in pb.workflow_stages:
        stage_dict[stage.id] = deepcopy(stage.config)
        stage_dict[stage.id]['services'] = dict()

    log.info('stage_dict: %s', json.dumps(stage_dict, indent=2))

    while True:

        # Start stages.
        log.info('*** Considering workflow stages for execution....')
        for stage in pb.workflow_stages:

            log.info('workflow stage: %s', stage.id)
            log.info('A. stage_dict keys: %s', stage_dict.keys())
            stage_data = stage_dict[stage.id]

            # Check if we can start this stage.
            stage_data['start'] = False
            log.info('  stage status %s', stage_data['status'])

            if stage_data['status'] == 'none':
                log.info('  dependencies: %s', stage.dependencies)
                if not stage.dependencies:
                    stage_data['start'] = True
                else:
                    dependency_status = []
                    ii = 0
                    for dependency in stage.dependencies:
                        # log.debug('  [%d] %s', ii, type(dependency))
                        # log.debug('  [%d] %s', ii, dependency)
                        # log.debug('  [%d] %s', ii, dependency.config)
                        log.info('   [%d] - %s, %s, %s', ii,
                                 dependency['type'], dependency['value'],
                                 dependency['condition'])
                        dependency_status.append(
                            stage_dict[dependency['value']]['status'] == 'complete')
                        ii += 1
                    stage_data['start'] = all(dependency_status)

            log.info('Start stage? %s',
                     ("true" if stage_data['start'] else "false"))

            if stage_data['start']:
                # Configure EE (set up templates)
                log.info('Configuring EE.')
                args_template = jinja2.Template(stage.args_template)
                log.debug('Args template: %s', stage.args_template)
                stage_params = pb.workflow_parameters[stage.id]
                template_params = {**stage.config, **stage_params}
                log.debug('template parameters: %s', template_params)
                args = args_template.render(stage=template_params)
                log.debug("Rendered args: '%s'", args)
                log.debug('Rendered args type: %s', type(args))
                args = json.dumps(json.loads(args))
                compose_template = jinja2.Template(stage.compose_template)
                compose_str = compose_template.render(stage=dict(args=args))
                log.info('COMPOSE_STR: {}'.format(compose_str))

                # Run the compose file
                service_ids = docker.create_services(compose_str)
                for service_id in service_ids:
                    stage_data['services'][service_id] = {}
                    log.info('Created Services: {}'.format(service_ids))
                    stage_data['services'][service_id] = dict(
                        name=docker.get_service_name(service_id),
                        status='running',
                        complete=False
                    )
                stage_data["status"] = 'running'

            # Check and update stage status
            log.info('Checking and updating stage status.')
            service_status_complete = []
            for service_id, service_dict in stage_data['services'].items():
                service_state = docker.get_service_state(service_id)
                log.debug('checking service status %s = %s', service_id,
                          service_state)
                if service_state == 'shutdown':
                    docker.delete_service(service_id)
                service_dict['status'] = service_state
                service_dict['complete'] = (service_state == 'shutdown')
                service_status_complete.append(service_dict['complete'])
                log.info('Status of service %s (id=%s) = %s',
                         service_dict['name'], service_id,
                         service_dict['status'])
                if all(service_status_complete):
                    stage_data['status'] = "complete"

        # Should I abort.
        # ask the database if the abort flag on this PB is set.
        # if abort:
        #   kill everything
        #   break

        # Check if all stages are complete, if so end the PBC by breaking
        # out of the while loop
        log.info('*** Check if workflow is complete ...')
        log.info('B. stage_dict keys: %s', stage_dict.keys())
        complete_stages = []
        for stage_id, stage_config in stage_dict.items():
            log.debug('stage status %s = %s', stage_id, stage_config['status'])
            complete_stages.append((stage_config['status'] == 'complete'))
        log.debug(' complete_stages = %s', complete_stages)
        if all(complete_stages):
            log.info('PB complete!')
            break
        log.info('C. stage_dict keys: %s', stage_dict.keys())

        time.sleep(1)

    log.info('Exiting PBC.')


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'version')
def version():
    """."""
    from .__init__ import __version__
    return __version__


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'add')
def add(a, b):
    """."""
    return a + b


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'execute_processing_block')
def execute_processing_block(pb_id: str):
    """Execute a processing block.

    Args:
        pb_id (str): The PB id for the PBC

    """
    log = logging.getLogger('sip')
    log.propagate = False  # FIXME(BMo) Make propagate a option on
                           # init_logger (default = False)?

    log = logging.getLogger('sip.ec.pbc')

    log.info('**** Executing Processing block: %s! ****', pb_id)
    log.info('Starting workflow ... ')

    pb = ProcessingBlock(pb_id)
    docker = DockerClient()

    workflow_stages = pb.workflow_stages
    running_service_ids = []

    while True:

        # # Check dependencies and get list of stages ready to start.
        # # ...
        # while True:
        #     for service_id in running_service_ids:
        #         service_state = docker.get_service_state(service_id)
        #         log.info("Running Docker Services: {}".format(service_id))
        #         if service_state == 'shutdown':
        #             docker.delete_service(service_id)
        #             log.info("Docker Services Deleted: {}".format(service_id))
        #             running_service_ids.remove(service_id)
        #         # if service is complete:
        #         #     del run_service_id[service_id]
        #
        #     break

        # Check if complete
        stages = [workflow_stages[0]]

        # Start stages.
        for stage in stages:
            # Configure EE
            log.info('workflow stage: %s', stage.id)
            log.info('xxx %s', stage.args_template)
            args_template = jinja2.Template(stage.args_template)
            log.info('xxx3 %s', json.dumps(stage.config))
            log.info('{}'.format(pb.workflow_parameters))
            stage_params = pb.workflow_parameters[stage.id]
            args = args_template.render(stage={**stage.config, **stage_params})
            args = json.dumps(json.loads(args))
            log.info('**********')
            log.info('ARGS: %s', args)

            compose_template = jinja2.Template(stage.compose_template)
            log.info('xxx1  %s', stage.compose_template)
            compose_str = compose_template.render(stage=dict(args=args))
            log.info('**********')
            log.info('COMPOSE_STR: {}'.format(compose_str))

            # Run the compose file
            service_ids = docker.create_services(compose_str)
            for service_ids in service_ids:
                log.info('Created Services: {}'.format(service_ids))
            running_service_ids.append(service_ids)
            log.info("Running Service IDS: {}".format(running_service_ids))
            # Update DB status
            # TODO (NJT): Need to update the state into the database

        # Check the state of the running services
        while running_service_ids:
            for service_id in running_service_ids:
                service_state = docker.get_service_state(service_id)
                log.info("Running Docker Services: {}".format(service_id))
                if service_state == 'shutdown':
                    docker.delete_service(service_id)
                    log.info("Docker Services Deleted: {}".format(service_id))
                    running_service_ids.remove(service_id)

        # if there are not more stages -> break
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
