# coding=utf-8
"""Unit tests of the Processing Block Controller.

http://docs.celeryproject.org/en/latest/userguide/testing.html
"""
import json
from os.path import dirname, join

from sip_config_db import ConfigDb
from sip_config_db.scheduling import SchedulingBlockInstance

from sip_pbc import execute_processing_block, version, echo
from sip_pbc.release import __version__

from ._test_utils import add_workflow_definitions

DB = ConfigDb()


def test_pbc_inspect_workers():
    """Test the Celery API for inspecting the Celery workers."""
    import celery
    inspect = celery.current_app.control.inspect()
    workers = inspect.ping()
    for worker in workers:
        assert not inspect.scheduled()[worker]
        assert not inspect.active()[worker]
        registered_tasks = inspect.registered_tasks()[worker]
        assert 'sip_pbc.tasks.execute_processing_block' in registered_tasks


def test_pbc_echo():
    """Test the SIP PBC echo method."""
    message = "Hello there!"
    result = echo.delay(message)
    assert result.get(timeout=3) == message


def test_pbc_version():
    """Test the SIP PBC version method."""
    result = version.delay()
    assert result.get(timeout=3) == __version__


def test_pbc_execute_workflow():
    """Test the SIP PBC execute_processing_block method."""
    DB.flush_db()
    data_dir = join(dirname(__file__), 'data')
    add_workflow_definitions(join(data_dir, 'workflow_definitions'))
    with open(join(data_dir, 'sbi_config_3.json')) as _file:
        sbi_config = json.load(_file)
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1
    assert pb_ids[0] == 'PB-20181116-sip-001'
    assert isinstance(pb_ids[0], str)

    result = execute_processing_block.delay(pb_ids[0])
    assert result.get() == 'completed'
