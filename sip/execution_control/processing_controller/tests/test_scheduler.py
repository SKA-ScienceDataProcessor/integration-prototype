# coding=utf-8
"""Unit tests of the Processing Controller Scheduler."""
import json
from os.path import dirname, join

from sip_config_db import ConfigDb
from sip_config_db.scheduling import SchedulingBlockInstance

from scheduler.scheduler import ProcessingBlockScheduler

from ._test_utils import add_workflow_definitions

DB = ConfigDb()


def test_processing_controller_scheduler_create():
    """Test creating the Scheduler after SBI data is already in the db."""
    DB.flush_db()
    data_dir = join(dirname(__file__), 'data')
    add_workflow_definitions(join(data_dir, 'workflow_definitions'))
    with open(join(data_dir, 'sbi_config_2.json')) as _file:
        sbi_config = json.load(_file)
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1
    assert pb_ids[0] == 'PB-20181116-sip-001'
    assert isinstance(pb_ids[0], str)

    scheduler = ProcessingBlockScheduler()

    assert scheduler.queue()
