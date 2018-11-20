# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task.

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import json
import logging
import os
import jinja2

from celery import Celery
from copy import deepcopy
from sip_config_db.scheduling import ProcessingBlock
from sip_docker_swarm import DockerClient, __version__
from sip_logging import init_logger

BROKER = os.getenv('CELERY_BROKER', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)


init_logger(log_level='DEBUG')


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'execute_processing_block')
def execute_processing_block(pb_id: str):
    """Execute a processing block.

    {
        "status": "none(change to: unknown?)" -> "running" -> "complete" (
        "aborted", "failed")
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

    # Coping workflow stages to a dict
    workflow_stage_dict = {}
    for stage in pb.workflow_stages:
        workflow_stage_dict[stage.id] = deepcopy(stage.config)
        workflow_stage_dict[stage.id]['services'] = dict()

    # For temporary use
    abort_flag = False

    while True:

        # Start stages.
        log.info('*** Considering workflow stages for execution.... ***')
        for workflow_stage in pb.workflow_stages:
            log.info('Workflow Stage: %s', workflow_stage.id)
            log.info('A. Workflow Stage Keys: %s', workflow_stage_dict.keys())
            stage_data = workflow_stage_dict[workflow_stage.id]

            # Check if we can start this stage.
            stage_data['start'] = False
            log.info('Workflow Stage Status %s', stage_data['status'])

            if stage_data['status'] == 'none':
                log.info('Dependencies: %s', workflow_stage.dependencies)
                if not workflow_stage.dependencies:
                    stage_data['start'] = True
                else:
                    dependency_status = []
                    # ii = 0
                    for dependency in workflow_stage.dependencies:
                        # log.debug('  [%d] %s', ii, type(dependency))
                        # log.debug('  [%d] %s', ii, dependency)
                        # log.debug('  [%d] %s', ii, dependency.config)
                        # log.info('[%d] - %s, %s, %s', ii, dependency['type'],
                        #          dependency['value'], dependency['condition'])
                        dependency_status.append(
                            workflow_stage_dict[dependency['value']][
                                'status'] == 'complete')
                        # ii += 1
                    stage_data['start'] = all(dependency_status)

            log.info('Start stage? %s',
                     ("true" if stage_data['start'] else "false"))

            if stage_data['start']:
                # Configure EE (set up templates)
                log.info('*** Configuring EE. ***')
                args_template = jinja2.Template(workflow_stage.args_template)
                # log.debug('Args template: %s', stage.args_template)
                stage_params = pb.workflow_parameters[workflow_stage.id]
                template_params = {**workflow_stage.config, **stage_params}
                # log.debug('template parameters: %s', template_params)
                args = args_template.render(stage=template_params)
                # log.debug("Rendered args: '%s'", args)
                # log.debug('Rendered args type: %s', type(args))
                args = json.dumps(json.loads(args))
                compose_template = jinja2.Template(
                    workflow_stage.compose_template)
                compose_str = compose_template.render(stage=dict(args=args))
                log.info('Compose String: {}'.format(compose_str))

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
            log.info('*** Checking and updating stage status. ***')
            service_status_complete = []

            if stage_data["status"] is not "complete":
                for service_id, service_dict in stage_data['services'].items():
                    service_state = docker.get_service_state(service_id)
                    # log.debug('checking service status %s = %s', service_id,
                    #           service_state)
                    if service_state == 'shutdown':
                        docker.delete_service(service_id)
                        # stage_data.pop()
                    service_dict['status'] = service_state
                    service_dict['complete'] = (service_state == 'shutdown')
                    service_status_complete.append(service_dict['complete'])
                    log.info('Status of service %s (id=%s) = %s',
                             service_dict['name'], service_id,
                             service_dict['status'])
                    if all(service_status_complete):
                        stage_data['status'] = "complete"

        # Ask the database if the abort flag or the PB is set.
        if abort_flag:
            log.info("*** Abort Flag has been triggered ***")
            for workflow_stage in pb.workflow_stages:
                for service_id, service_dict in \
                        workflow_stage_dict[workflow_stage.id][
                            'services'].items():
                    docker.delete_service(service_id)
                    log.info("Deleted Service Id %s", service_id)
            break

        # Check if all stages are complete, if so end the PBC by breaking
        # out of the while loop
        log.info('*** Check if workflow is complete ...')
        log.info('B. Workflow Stage Keys: %s', workflow_stage_dict.keys())
        complete_stages = []
        for stage_id, stage_config in workflow_stage_dict.items():
            log.info('Workflow Stage Status %s = %s', stage_id,
                     stage_config['status'])
            complete_stages.append((stage_config['status'] == 'complete'))
        # log.debug(' complete_stages = %s', complete_stages)
        if all(complete_stages):
            log.info('PB complete!')
            break
        log.info('C. Workflow Stage Keys: %s', workflow_stage_dict.keys())

    log.info('Exiting PBC.')


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'version')
def version():
    """."""
    from .__init__ import __version__
    return __version__
