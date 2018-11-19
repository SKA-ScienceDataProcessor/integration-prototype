# coding=utf-8
"""Module to generate test data for sbi and pb client.

FIXME(BMo) Move this to a method on the SchedulingBlockInstance object?
"""
import datetime
import json
from random import choice, randint
from typing import List, Union

from .. import DB
from ..scheduling import ProcessingBlock, SchedulingBlockInstance, \
    PB_VERSION, SBI_VERSION

PB_TYPES = [
    'realtime',
    'offline'
]

REALTIME_WORKFLOWS = [
    'vis_ingest_test'
]

OFFLINE_WORKFLOWS = [
    'ical_test'
]


def add_workflow_definitions(sbi_config: dict):
    """Add any missing SBI workflow definitions as placeholders.

    This is a utility function used in testing and adds mock / test workflow
    definitions to the database for workflows defined in the specified
    SBI config.

    Args:
        sbi_config (dict): SBI configuration dictionary.

    """
    registered_workflows = []
    for i in range(len(sbi_config['processing_blocks'])):
        workflow_config = sbi_config['processing_blocks'][i]['workflow']
        workflow_name = '{}:{}'.format(workflow_config['id'],
                                       workflow_config['version'])
        if workflow_name in registered_workflows:
            continue
        workflow_definition = dict(
            id=workflow_config['id'],
            version=workflow_config['version'],
            stages=[]
        )
        key = "workflow_definitions:{}:{}".format(workflow_config['id'],
                                                  workflow_config['version'])
        DB.set_hash_values(key, workflow_definition)
        registered_workflows.append(workflow_name)


def generate_version(max_major: int = 1, max_minor: int = 7,
                     max_patch: int = 15) -> str:
    """Select a random version.

    Args:
        max_major (int, optional) maximum major version
        max_minor (int, optional) maximum minor version
        max_patch (int, optional) maximum patch version

    Returns:
        str, Version String

    """
    major = randint(0, max_major)
    minor = randint(0, max_minor)
    patch = randint(0, max_patch)
    return '{:d}.{:d}.{:d}'.format(major, minor, patch)


def generate_sb(date: datetime.datetime, project: str,
                programme_block: str) -> dict:
    """Generate a Scheduling Block data object.

    Args:
        date (datetime.datetime): UTC date of the SBI
        project (str): Project Name
        programme_block (str): Programme

    Returns:
        str, Scheduling Block Instance (SBI) ID.

    """
    date = date.strftime('%Y%m%d')
    instance_id = randint(0, 9999)
    sb_id = 'SB-{}-{}-{:04d}'.format(date, project, instance_id)
    return dict(id=sb_id, project=project, programme_block=programme_block)


def generate_pb_config(pb_id: str,
                       pb_config: dict = None,
                       workflow_config: dict = None) -> dict:
    """Generate a PB configuration dictionary.

    Args:
        pb_id (str): Processing Block Id
        pb_config (dict, optional) PB configuration.
        workflow_config (dict, optional): Workflow configuration

    Returns:
        dict, PB configuration dictionary.

    """
    if workflow_config is None:
        workflow_config = dict()
    if pb_config is None:
        pb_config = dict()
    pb_type = pb_config.get('type', choice(PB_TYPES))
    workflow_id = workflow_config.get('id')
    if workflow_id is None:
        if pb_type == 'offline':
            workflow_id = choice(OFFLINE_WORKFLOWS)
        else:
            workflow_id = choice(REALTIME_WORKFLOWS)
    workflow_version = workflow_config.get('version', generate_version())
    workflow_parameters = workflow_config.get('parameters', dict())
    pb_data = dict(
        id=pb_id,
        version=PB_VERSION,
        type=pb_type,
        priority=pb_config.get('priority', randint(0, 10)),
        dependencies=pb_config.get('dependencies', []),
        resources_required=pb_config.get('resources_required', []),
        workflow=dict(
            id=workflow_id,
            version=workflow_version,
            parameters=workflow_parameters
        )
    )
    return pb_data


def generate_sbi_config(num_pbs: int = 3, project: str = 'sip',
                        programme_block: str = 'sip_demos',
                        pb_config: Union[dict, List[dict]] = None,
                        workflow_config:
                        Union[dict, List[dict]] = None,
                        register_workflows=False) -> dict:
    """Generate a SBI configuration dictionary.

    Args:
        num_pbs (int, optional): Number of Processing Blocks (default = 3)
        project (str, optional): Project to associate the SBI with.
        programme_block (str, optional): SBI programme block
        pb_config (dict, List[dict], optional): PB configuration
        workflow_config (dict, List[dict], optional): Workflow configuration
        register_workflows (bool, optional): If true also register workflows.

    Returns:
        dict, SBI configuration dictionary

    """
    if isinstance(workflow_config, dict):
        workflow_config = [workflow_config]
    if isinstance(pb_config, dict):
        pb_config = [pb_config]
    utc_now = datetime.datetime.utcnow()
    pb_list = []
    for i in range(num_pbs):
        pb_id = ProcessingBlock.get_id(utc_now)
        if workflow_config is not None:
            _workflow_config = workflow_config[i]
        else:
            _workflow_config = None
        if pb_config is not None:
            _pb_config = pb_config[i]
        else:
            _pb_config = None
        pb_dict = generate_pb_config(pb_id, _pb_config, _workflow_config)
        pb_list.append(pb_dict)
    sbi_config = dict(
        id=SchedulingBlockInstance.get_id(utc_now, project),
        version=SBI_VERSION,
        scheduling_block=generate_sb(utc_now, project, programme_block),
        processing_blocks=pb_list
    )
    if register_workflows:
        add_workflow_definitions(sbi_config)
    return sbi_config


def generate_sbi_json(num_pbs: int = 3, project: str = 'sip',
                      programme_block: str = 'sip_demos',
                      pb_config: Union[dict, List[dict]] = None,
                      workflow_config:
                      Union[dict, List[dict]] = None,
                      register_workflows=True) -> str:
    """Return a JSON string used to configure an SBI."""
    return json.dumps(generate_sbi_config(num_pbs, project, programme_block,
                                          pb_config,
                                          workflow_config, register_workflows))
