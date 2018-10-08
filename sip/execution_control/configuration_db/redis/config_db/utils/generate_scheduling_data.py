# coding=utf-8
"""Module to generate test data for sbi and pb client."""
import datetime
from random import randint, choice

import namesgenerator

# TODO(NJT) Needs to re-written according to the new schema.
# TODO - Pattern in the schema needs to be updated

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


def generate_sb_id(date: datetime.datetime, project: str) -> str:
    """Generate a Scheduling Block Instance (SBI) ID.

    Args:
        date (datetime.datetime): UTC date of the SBI
        project (str): Project Name

    Returns:
        str, Scheduling Block Instance (SBI) ID.

    """
    date = date.strftime('%Y%m%d')
    instance_id = randint(0, 9999)
    return '{}-{}-sb{:04d}'.format(date, project, instance_id)


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
    return '{}-{}-sbi{:04d}'.format(date, project, instance_id)


def generate_pb_id(workflow_type: str) -> str:
    """Generate a Processing Block (PB) Instance ID.

    Args:
        workflow_type (str): Workflow Type

    Returns:
        str, Processing Block ID

    """
    return 'pb-{}{:03d}'.format(workflow_type, randint(0, 100))


def generate_pb_config(pb_id: str, workflow_type: str) -> dict:
    """Generate a PB configuration dictionary.

    Args:
        pb_id (str): Processing Block Id
        workflow_type (str): Workflow Type

    Returns:
        dict, PB configuration dictionary.

    """
    workflow = []
    workflow_data = dict(
        workflow_type=workflow_type,
        resource_requirement=dict(
            storage_type=choice(STORAGE_TYPES),
            volume='mount',
            cpu=2
        ),
        assigned_resources=dict(),
        execution_engine_parameters=dict(),
        configuration=dict()
    )
    workflow.append(workflow_data)
    pb_data = dict(
        id=pb_id,
        type=choice(PB_TYPES),
        template="",
        priority=randint(0, 10),
        workflow=workflow
    )
    return pb_data


def generate_sbi_config(num_pbs: int = 3) -> dict:
    """Generate a SBI configuration dictionary.

    Args:
        num_pbs (int, optional): Number of Processing Blocks (default = 3)

    Returns:
        dict, SBI configuration dictionary

    """
    utc_now = datetime.datetime.utcnow()
    date_time = utc_now.strftime('%Y/%m/%d %H:%M:%S')
    project = generate_project()
    sbi_pb_config = []
    for _ in range(num_pbs):
        workflow_type = choice(WORKFLOW_TYPES)
        pb_id = generate_pb_id(workflow_type)
        sbi_pb_config.append(generate_pb_config(pb_id, workflow_type))
    sbi_config = dict(
        id=generate_sbi_id(utc_now, project),
        scheduling_block_id=generate_sb_id(utc_now, project),
        sub_array_id='subarray{}'.format(randint(1, 15)),
        date_time=date_time,
        project=project,
        name=namesgenerator.get_random_name(),
        processing_blocks=sbi_pb_config
    )
    return sbi_config
