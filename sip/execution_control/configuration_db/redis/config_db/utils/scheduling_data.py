# coding=utf-8
"""Execution Control Scheduling Data Model resources API.

This module is used by the Processing Controller Services for interacting with
Scheduling Block Instances, Processing Blocks, and Sub-arrays data models
used to Schedule the SDP processing.
"""

from config_db import SchedulingBlockDbClient
from config_db import ProcessingBlockDbClient
from .generate_scheduling_data import generate_sbi_config

sbi_db = SchedulingBlockDbClient()
pb_db = ProcessingBlockDbClient()


def add_sbi():
    """Add scheduling block data."""

    sbi_config = generate_sbi_config(num_pbs=1)
    sbi_db.add_sbi(sbi_config)


def cancel_sbi(sbi_id):
    """Cancel a SBI.

    Args:
        sbi_id (str): the SBI Id

    """
    sbi_db.cancel_sbi(sbi_id)


def cancel_pb(pb_id):
    """Cancel a Processing Block.

    Args:
        pb_id (str): the PD ID

    """
    pb_db.cancel_processing_block(pb_id)


if __name__== '__main__':
    add_sbi()

