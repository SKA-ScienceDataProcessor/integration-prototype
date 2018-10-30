# coding=utf-8
"""Module to generate test data for sbi and pb client."""
import datetime
from random import randint, choice
from ..sbi import SchedulingBlockInstance as sbi
from ..pb import ProcessingBlock as pb

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


SBI_VERSION = "0.4.0"
PB_VERSION = "0.4.0"


def generate_version(max_major: int = 1, max_minor: int = 7,
                     max_patch: int = 15):
    """Select a random version

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


def generate_pb_config(pb_id: str) -> dict:
    """Generate a PB configuration dictionary.

    Args:
        pb_id (str): Processing Block Id

    Returns:
        dict, PB configuration dictionary.

    """
    pb_type = choice(PB_TYPES)
    if pb_type == 'offline':
        workflow_id = choice(OFFLINE_WORKFLOWS)
    else:
        workflow_id = choice(REALTIME_WORKFLOWS)
    pb_data = dict(
        id=pb_id,
        version=PB_VERSION,
        type=pb_type,
        priority=randint(0, 10),
        dependencies=[],
        workflow=dict(
            id=workflow_id,
            version=generate_version(),
            parameters=dict()
        )
    )
    return pb_data


def generate_sbi_config(num_pbs: int = 3, project: str = 'sip',
                        programme_block: str = 'sip_demos') -> dict:
    """Generate a SBI configuration dictionary.

    Args:
        num_pbs (int, optional): Number of Processing Blocks (default = 3)
        project (str, optional): Project to associate the SBI with.
        programme_block (str, optional): Programme block to associate the SBI
                                         with

    Returns:
        dict, SBI configuration dictionary

    """
    utc_now = datetime.datetime.utcnow()
    pb_list = []
    for _ in range(num_pbs):
        pb_id = pb.get_id(utc_now)
        pb_config = generate_pb_config(pb_id)
        pb_list.append(pb_config)
    # print(json.dumps(pb_list, indent=2))

    sbi_config = dict(
        id=sbi.get_id(utc_now, project),
        version=SBI_VERSION,
        scheduling_block=generate_sb(utc_now, project, programme_block),
        processing_blocks=pb_list
    )
    # print('=' * 80)
    # print('=' * 80)
    # print('=' * 80)
    # print(json.dumps(sbi_config, indent=2))
    # print('=' * 80)
    # print('=' * 80)
    # print('=' * 80)

    return sbi_config
