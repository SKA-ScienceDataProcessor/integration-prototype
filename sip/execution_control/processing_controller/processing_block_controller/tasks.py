# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task.

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import json
import os
import jinja2
import time

import yaml

from .release import LOG, __service_name__, __version__
from celery import Celery
from copy import deepcopy
from sip_config_db.scheduling import ProcessingBlock, ProcessingBlockList
from sip_docker_swarm import DockerClient
from sip_docker_swarm import __version__ as sip_swarm_api_version
from sip_logging import init_logger


BROKER = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'version')
def version():
    """Return the PBC version."""
    init_logger(show_log_origin=True, p3_mode=False)
    LOG.info('Getting the PBC version! version = %s', __version__)
    return __version__


@APP.task(name='processing_controller.processing_block_controller.tasks.'
               'execute_processing_block')
def execute_processing_block(pb_id: str):
    """Execute a processing block.

    Args:
        pb_id (str): The PB id for the PBC

    """
    init_logger(show_log_origin=True, propagate=False, p3_mode=False)
    LOG.info('+' * 60)
    LOG.info('+' * 60)
    LOG.info('+ Executing Processing block: %s!', pb_id)
    LOG.info('+' * 60)
    LOG.info('+' * 60)
    LOG.info('Using docker swarm api version: %s', sip_swarm_api_version)

    pb = ProcessingBlock(pb_id)

    LOG.info('Starting workflow %s %s', pb.workflow_id, pb.workflow_version)

    pb.set_status('running')
    docker = DockerClient()

    # Coping workflow stages to a dict
    workflow_stage_dict = {}
    for stage in pb.workflow_stages:
        workflow_stage_dict[stage.id] = deepcopy(stage.config)
        workflow_stage_dict[stage.id]['services'] = dict()

    # For temporary use
    abort_flag = False

    while True:
        time.sleep(0.1)

        # Start stages.
        # LOG.info('*** Considering workflow stages for execution.... ***')
        for workflow_stage in pb.workflow_stages:
            # LOG.info('Workflow Stage: %s', workflow_stage.id)
            # LOG.info('A. Workflow Stage Keys: %s', workflow_stage_dict.keys())
            stage_data = workflow_stage_dict[workflow_stage.id]

            # Check if we can start this stage.
            stage_data['start'] = False
            # LOG.info('Workflow Stage Status %s', stage_data['status'])

            if stage_data['status'] == 'none':
                # LOG.info('Dependencies: %s', workflow_stage.dependencies)
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

            # LOG.info('Start stage? %s',
            #          ("true" if stage_data['start'] else "false"))

            if stage_data['start']:
                # Configure EE (set up templates)
                LOG.info(' Starting workflow stage: %s', workflow_stage.id)
                LOG.info('^' * 60)
                LOG.info('Configuring EE templates.')
                args_template = jinja2.Template(workflow_stage.args_template)
                # log.debug('Args template: %s', stage.args_template)
                stage_params = pb.workflow_parameters[workflow_stage.id]
                template_params = {**workflow_stage.config, **stage_params}
                # log.debug('template parameters: %s', template_params)
                args = args_template.render(stage=template_params)
                # log.debug("Rendered args: '%s'", args)
                # log.debug('Rendered args type: %s', type(args))
                LOG.info('Resolving workflow script arguments.')

                args = json.dumps(json.loads(args))
                compose_template = jinja2.Template(
                    workflow_stage.compose_template)
                compose_str = compose_template.render(stage=dict(args=args))

                # Prefix service names with the PB id
                compose_dict = yaml.load(compose_str)
                service_names = compose_dict['services'].keys()
                new_service_names = [
                    '{}_{}_{}'.format(pb_id, pb.workflow_id, name)
                    for name in service_names]
                for new, old in zip(new_service_names, service_names):
                    compose_dict['services'][new] = \
                        compose_dict['services'].pop(old)
                compose_str = yaml.dump(compose_dict)

                # Run the compose file
                service_ids = docker.create_services(compose_str)
                LOG.info('Staring workflow containers:')
                for service_id in service_ids:
                    service_name = docker.get_service_name(service_id)
                    LOG.info("  %s, %s ", service_name, service_id)
                    stage_data['services'][service_id] = {}
                    LOG.info('Created Services: {}'.format(service_ids))
                    stage_data['services'][service_id] = dict(
                        name=docker.get_service_name(service_id),
                        status='running',
                        complete=False
                    )
                stage_data["status"] = 'running'

            # Check and update stage status
            # LOG.info('*** Checking and updating stage status. ***')
            service_status_complete = []

            # FIXME(BMo) is not "complete" -> is "running"
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
                    # LOG.info('Status of service %s (id=%s) = %s',
                    #          service_dict['name'], service_id,
                    #          service_dict['status'])
                    if all(service_status_complete):
                        LOG.info('Workflow stage service %s complete!',
                                 workflow_stage.id)
                        stage_data['status'] = "complete"

        # TODO(BMo) Ask the database if the abort flag on the PB is set.
        if abort_flag:
            LOG.info("*** Abort Flag has been triggered ***")
            for workflow_stage in pb.workflow_stages:
                for service_id, service_dict in \
                        workflow_stage_dict[workflow_stage.id][
                            'services'].items():
                    docker.delete_service(service_id)
                    LOG.info("Deleted Service Id %s", service_id)
            break

        # Check if all stages are complete, if so end the PBC by breaking
        # out of the while loop
        complete_stages = []
        for stage_id, stage_config in workflow_stage_dict.items():
            # LOG.info('Workflow Stage Status %s = %s', stage_id,
            #          stage_config['status'])
            complete_stages.append((stage_config['status'] == 'complete'))
        # log.debug(' complete_stages = %s', complete_stages)
        if all(complete_stages):
            LOG.info('PB workflow complete!')
            break
        # LOG.info('C. Workflow Stage Keys: %s', workflow_stage_dict.keys())

    pb_list = ProcessingBlockList()
    pb_list.set_complete(pb_id)
    pb.set_status('completed')
    LOG.info('-' * 60)
    LOG.info('-' * 60)
    LOG.info('- Destroying PBC for %s', pb_id)
    LOG.info('-' * 60)
    LOG.info('-' * 60)

