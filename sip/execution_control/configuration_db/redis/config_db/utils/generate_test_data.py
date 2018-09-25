# coding=utf-8
"""Module to generate test data for sbi and pb client."""
from uuid import uuid4
import datetime
from random import randint, choice

import namesgenerator

# TODO(NJT) Needs to re-written according to the new schema.
# TODO - Pattern in the schema needs to be updated

PB_TYPES = [
    'real-time',
    'offline'
]

WORKFLOW_TYPES = [
    'ingest_vis',
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
    return 'project_{:03d}'.format(randint(0, 100))


def generate_sbi_id(date: datetime.datetime, project: str, sb_id: str) -> str:
    """Generate a Scheduling Block Instance (SBI) ID.

    Args:
        date (datetime.datetime): UTC date of the SBI
        project (str): Project Name
        sb_id (str): Scheduling Block ID

    Returns:
        str, Scheduling Block Instance (SBI) ID.

    """
    date = date.strftime('%Y%m%d')
    instance_id = randint(0, 9999)
    return '{}-{}-{}-{:04d}'.format(date, project, sb_id, instance_id)


def generate_pb_id() -> str:
    """Generate a Processing Block (PB) Instance ID.

    Returns:
        str, Processing Block ID

    """
    return 'pb_{}'.format(str(uuid4())[:8])


def generate_pb_config(pb_id: str) -> dict:
    """Generate a PB configuration dictionary.

    Args:
        pb_id (str): Processing Block Id

    Returns:
        dict, PB configuration dictionary.

    """
    pb_data = dict(
        id=pb_id,
        type=choice(PB_TYPES),
        status='',
        workflow_type=choice(WORKFLOW_TYPES),
        priority=randint(0, 10),
        resources_required=dict(),
        resources_assigned=dict(),
        workflow_template=dict(),
        workflow_stages=list()
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
    date = utc_now.strftime('%Y/%m/%d %H:%M:%S')
    project = generate_project()
    sb_id = str(uuid4())[:8]
    sbi_pb_config = {}
    pb_ids = []
    for _ in range(num_pbs):
        pb_id = generate_pb_id()
        sbi_pb_config[pb_id] = generate_pb_config(pb_id)
        pb_ids.append(pb_id)
    sbi_config = dict(
        id=generate_sbi_id(utc_now, project, sb_id),
        scheduling_block_id=sb_id,
        sub_array_id=randint(-1, 15),
        date=date,
        status='',
        project=project,
        name=namesgenerator.get_random_name(),
        processing_block_ids=pb_ids,
        processing_blocks=sbi_pb_config
    )
    return sbi_config
