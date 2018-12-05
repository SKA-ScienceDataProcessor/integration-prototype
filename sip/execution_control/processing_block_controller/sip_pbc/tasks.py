# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task.

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import json
import os
import time
from copy import deepcopy

import jinja2
import yaml
from celery import Celery

from sip_config_db.scheduling import ProcessingBlock, ProcessingBlockList
from sip_config_db.scheduling.workflow_stage import WorkflowStage
from sip_docker_swarm import DockerClient, __version__ as sip_swarm_api_version
from sip_logging import init_logger
from .release import LOG, __version__

BROKER = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)


@APP.task
def echo(value: str):
    """Echo a string."""
    return value


@APP.task
def version():
    """Return the PBC version."""
    init_logger(show_log_origin=True, p3_mode=False)
    LOG.info('Getting the PBC version! version = %s', __version__)
    return __version__


def _start_workflow_stages(pb: ProcessingBlock, pb_id,
                           workflow_stage_dict, workflow_stage: WorkflowStage,
                           docker: DockerClient):
    """."""
    # FIXME(BMo) replace pb_id argument, get this from the pb instead!
    stage_data = workflow_stage_dict[workflow_stage.id]
    stage_data['start'] = False

    # Determine if the stage can be started.
    if stage_data['status'] == 'none':
        if not workflow_stage.dependencies:
            stage_data['start'] = True
        else:
            dependency_status = []
            for dependency in workflow_stage.dependencies:
                dependency_status.append(
                    workflow_stage_dict[dependency['value']][
                        'status'] == 'complete')
                # ii += 1
            stage_data['start'] = all(dependency_status)

    # Start the workflow stage.
    if stage_data['start']:
        # Configure EE (set up templates)
        LOG.info('-- Starting workflow stage: %s --', workflow_stage.id)
        LOG.info('Configuring EE templates.')
        args_template = jinja2.Template(workflow_stage.args_template)
        stage_params = pb.workflow_parameters[workflow_stage.id]
        template_params = {**workflow_stage.config, **stage_params}
        args = args_template.render(stage=template_params)
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
            LOG.info('Created Services: %s', service_ids)
            stage_data['services'][service_id] = dict(
                name=docker.get_service_name(service_id),
                status='running',
                complete=False
            )
        stage_data["status"] = 'running'


def _update_workflow_stages(stage_data, workflow_stage: WorkflowStage,
                            docker: DockerClient):
    """."""
    # Check and update stage status
    # LOG.info('*** Checking and updating stage status. ***')
    service_status_complete = []

    # FIXME(BMo) is not "complete" -> is "running"
    if stage_data["status"] != "complete":
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


def _abort_workflow(pb, workflow_stage_dict, docker):
    """."""
    # TODO(BMo) Ask the database if the abort flag on the PB is set.
    _abort_flag = False
    if _abort_flag:
        for workflow_stage in pb.workflow_stages:
            for service_id, _ in \
                    workflow_stage_dict[workflow_stage.id]['services'].items():
                docker.delete_service(service_id)
                LOG.info("Deleted Service Id %s", service_id)
        return True
    return False


def _workflow_complete(workflow_stage_dict):
    """."""
    # Check if all stages are complete, if so end the PBC by breaking
    # out of the while loop
    complete_stages = []
    for _, stage_config in workflow_stage_dict.items():
        complete_stages.append((stage_config['status'] == 'complete'))
    if all(complete_stages):
        LOG.info('PB workflow complete!')
        return True
    return False


@APP.task
def execute_processing_block(pb_id: str):
    """Execute a processing block.

    Args:
        pb_id (str): The PB id for the PBC

    """
    init_logger('sip', show_log_origin=True, propagate=False, p3_mode=False)
    LOG.info('+' * 40)
    LOG.info('+ Executing Processing block: %s!', pb_id)
    LOG.info('+' * 40)
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

    # Loop until workflow stages are complete.
    while True:
        time.sleep(0.1)

        for workflow_stage in pb.workflow_stages:

            _start_workflow_stages(pb, pb_id, workflow_stage_dict,
                                   workflow_stage, docker)

            _update_workflow_stages(workflow_stage_dict[workflow_stage.id],
                                    workflow_stage, docker)

        if _abort_workflow(pb, workflow_stage_dict, docker):
            break

        if _workflow_complete(workflow_stage_dict):
            break

    pb_list = ProcessingBlockList()
    pb_list.set_complete(pb_id)
    pb.set_status('completed')
    LOG.info('-' * 40)
    LOG.info('- Destroying PBC for %s', pb_id)
    LOG.info('-' * 40)
    return pb.status
