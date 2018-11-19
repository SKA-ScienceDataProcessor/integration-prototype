# coding=utf-8
"""Module to generate test data for sbi and pb client."""
import datetime
from random import randint, choice

import namesgenerator

# TODO(NJT) Needs to re-written according to the new schema.
# TODO - Pattern in the schema needs to be updated

TELESCOPE_TYPES = [
    'ska1_low'
]

VOLUME_TYPES = [
    'mount',
    'bind',
    'ceph'
]

COMPUTE_TYPES = [
    'compute_a',
    'compute_b',
]

PB_TYPES = [
    'real-time',
    'offline'
]

STORAGE_TYPES = [
    'hot',
    'cold'
]

WORKFLOW_TYPES = [
    'ingest',
    'ical',
    'dprepa',
    'dprepb',
    'dprepc',
    'dprepd'
]


def generate_project() -> str:
    """Generate a random project name.

    Returns:
        str, project name.

    """
    return 'skasip'


def generate_sb(date: datetime.datetime, project: str) -> str:
    """Generate a Scheduling Block dictionary.

    Args:
        date (datetime.datetime): UTC date of the SB
        project (str): Project Name

    Returns:
        str, Scheduling Block .

    """
    date = date.strftime('%Y%m%d')
    instance_id = randint(0, 9999)
    sb_id = 'SB-{}-{}-{:04d}'.format(date, project, instance_id)

    scheduling_block_data = dict(
        id=sb_id,
        project=project,
        telescope=choice(TELESCOPE_TYPES),
        program_block='sip_demos'
    )
    return scheduling_block_data


def generate_sbi_id(date: datetime.datetime, project: str) -> str:
    """Generate a Scheduling Block Instance (SBI) ID.

    Args:
        date (datetime.datetime): UTC date of the SBI
        project (str): Project Name

    Returns:
        str, Scheduling Block Instance (SBI) ID.

    """
    date = date.strftime('%Y%m%d')
    instance_id = randint(0, 9999)
    return 'SBI-{}-{}-{:04d}'.format(date, project, instance_id)


def generate_scans(date: datetime.datetime):
    """Generate a Scans dictionary.

    Args:
        date (datetime.datetime): UTC date of the SBI

    Returns:
        str, Scans.

    """
    date = date.strftime('%Y%m%d')
    instance_id = randint(0, 99)
    scan_id = 'scan-{}-{:02d}'.format(date, instance_id)

    scan_data = dict(
        id=scan_id,
    )
    return scan_data


def generate_workflow_id(workflow_type: str):
    """Generate workflow ID.

    Args:
        workflow_type (str): Workflow Type
        w_stage_type (str): Workflow stage type

    Returns:
          str, workflow id
    """
    instance_id = randint(0, 99)
    # Need to fix this
    workflow_stage_id = '{}-{:02d}'.format(workflow_type, instance_id)

    return workflow_stage_id


def generate_workflow_stage_id(workflow_type: str, w_stage_type: str):
    """Generate workflow ID.

    Args:
        workflow_type (str): Workflow Type
        w_stage_type (str): Workflow stage type

    Returns:
          str, workflow id
    """
    instance_id = randint(0, 99)
    workflow_stage_id = '{}-{}-{:02d}'.format(workflow_type,
                                              w_stage_type, instance_id)

    return workflow_stage_id


def generate_pb_id(workflow_type: str, date: datetime.datetime) -> str:
    """Generate a Processing Block (PB) Instance ID.

    Args:
        workflow_type (str): Workflow Type
        date (datetime.datetime): UTC date of the PB

    Returns:
        str, Processing Block ID

    """

    date = date.strftime('%Y%m%d')
    return 'PB-{}-{}-{:03d}'.format(date, workflow_type, randint(0, 100))


def generate_resource_id():
    """Generate resources required ID.


    Returns:
        str, resource required ID.
    """

    return 'node:p3-{}-{:03d}'.format(choice(COMPUTE_TYPES), randint(0, 100))


def generate_overall_resources(storage_type: str, volume_type: str):
    """Generate an overall resources required.

    Args:
        storage_type (str): Storage Type
        volume_type (str): Volume Type

    Returns:
        dict, overall resource required dictionary.

    """

    resources_required = dict(
        id='buffer-{}-{}-{:03d}'.format(storage_type, volume_type,
                                        randint(0, 100)),
        value='{:03d}GB'.format(randint(0, 100)),
        parameters=dict()
    )

    return resources_required


def generate_resources_required(storage_type: str, volume_type: str,
                                stage: bool = True) -> dict:
    """Generate resource requirement dictionary.

    Args:
        storage_type (str): Storage Type
        volume_type (str): Volume Type
        stage (bool): Workflow Exclusive

    Returns:
        dict, resource requirement dictionary
    """
    if not stage:
        parameters = dict(
            exclusive=False
        )
    else:
        parameters = dict(
            exclusive=stage,
            storage_type=storage_type,
            volume=volume_type,
            cpu=randint(0, 10)
        )

    resources_required = dict(
        id=generate_resource_id(),
        value=3,
        parameters=parameters
    )

    return resources_required


def generate_pb_config(pb_id: str, workflow_type: str, version: str) -> dict:
    """Generate a PB configuration dictionary.

    Args:
        pb_id (str): Processing Block Id
        workflow_type (str): Workflow Type
        version (str): Version of the data

    Returns:
        dict, PB configuration dictionary.

    """
    workflow_stages = []
    storage_type = choice(STORAGE_TYPES)
    volume_type = choice(VOLUME_TYPES)

    w_stage_type = "setup"
    workflow_setup = dict(
        id=generate_workflow_stage_id(workflow_type, w_stage_type),
        type=w_stage_type,
        version=version,
        dependencies=[],
        resources_required=generate_resources_required(storage_type,
                                                       volume_type),
        assigned_resources=dict(),
        ee_config=dict(
            type="docker_swarm",
            compose_template="/workflow_templates/startup.yaml.j2"
        ),
        app_config=dict(
            args_template="/workflow_applications/start.yaml.j2"
        ),
    )
    workflow_stages.append(workflow_setup)

    w_stage_type = "processing"
    workflow_processing = dict(
        id=generate_workflow_stage_id(workflow_type, w_stage_type),
        type=w_stage_type,
        version=version,
        dependencies=[],
        resources_required=generate_resources_required(storage_type,
                                                       volume_type),
        assigned_resources=dict(),
        ee_config=dict(
            type="docker_swarm",
            compose_template="/workflow_templates/processing.yaml.j2"
        ),
        app_config=dict(
            args_template="/workflow_applications/process.yaml.j2"
        ),
    )
    workflow_stages.append(workflow_processing)

    w_stage_type = "cleanup"
    workflow_cleanup = dict(
        id=generate_workflow_stage_id(workflow_type, w_stage_type),
        type=w_stage_type,
        version=version,
        dependencies=[],
        resources_required=generate_resources_required(
            storage_type, volume_type, stage=False),
        assigned_resources=dict(),
        ee_config=dict(
            type="docker_swarm",
            compose_template=".workflow_templates/cleanup.yaml.j2"
        ),
        app_config=dict()
    )
    workflow_stages.append(workflow_cleanup)

    # Generating PB data
    pb_data = dict(
        id=pb_id,
        version=version,
        type=choice(PB_TYPES),
        priority=randint(0, 10),
        resources_required=generate_overall_resources(storage_type, volume_type),
        workflow_id=generate_workflow_id(workflow_type),
        workflow_version=version,
        workflow_stages=workflow_stages
    )
    return pb_data


def generate_sbi_config(num_pbs: int = 3) -> dict:
    """Generate a SBI configuration dictionary.

    Args:
        num_pbs (int, optional): Number of Processing Blocks (default = 3)

    Returns:
        dict, SBI configuration dictionary

    """
    project = generate_project()
    utc_now = datetime.datetime.utcnow()
    date_time = utc_now.strftime('%Y%m%d %H:%M:%S')
    version = "1.0.0"
    sbi_pb_config = []

    for _ in range(num_pbs):
        workflow_type = choice(WORKFLOW_TYPES)
        pb_id = generate_pb_id(workflow_type, utc_now)
        sbi_pb_config.append(generate_pb_config(pb_id, workflow_type, version))
    sbi_config = dict(
        id=generate_sbi_id(utc_now, project),
        version=version,
        scheduling_block=generate_sb(utc_now, project),
        subarray='subarray-{}'.format(randint(1, 15)),
        date_time=date_time,
        scans=generate_scans(utc_now),
        # name=namesgenerator.get_random_name(),
        processing_blocks=sbi_pb_config
    )

    return sbi_config
