# coding=utf-8
"""Unit tests of the Processing Block Controller.

http://docs.celeryproject.org/en/latest/userguide/testing.html

FIXME(BMo) At the moment these tests require that the PBC has started.
           Its possible that this requirement is not needed using some
           Celery testing magic.

"""
import json
from os.path import dirname, join

import redis
import celery
import pytest

from sip_config_db import ConfigDb
from sip_config_db.scheduling import SchedulingBlockInstance

from sip_pbc import echo, execute_processing_block, version
from sip_pbc.release import __version__

from ._test_utils import add_workflow_definitions

DB = ConfigDb()


def test_pbc_inspect_workers():
    """Test the Celery API for inspecting the Celery workers."""
    try:
        celery.current_app.broker_connection().connect()
    except redis.exceptions.ConnectionError:
        pytest.fail('Failed to connect to broker: {}'
                    .format(celery.current_app.broker_connection().as_uri()),
                    pytrace=False)
    inspect = celery.current_app.control.inspect()
    workers = inspect.ping()
    if workers is None:
        pytest.skip('Unable to find any celery workers!')
    for worker in workers:
        assert not inspect.scheduled()[worker]
        assert not inspect.active()[worker]
        registered_tasks = inspect.registered_tasks()[worker]
        assert 'sip_pbc.tasks.execute_processing_block' in registered_tasks


def test_pbc_echo():
    """Test the SIP PBC echo method."""
    message = "Hello there!"
    result = echo.apply(args=(message,))
    assert result.get(timeout=3) == message


def test_pbc_version():
    """Test the SIP PBC version method."""
    result = version.apply()
    assert result.get(timeout=3) == __version__


def test_pbc_execute_workflow():
    """Test the SIP PBC execute_processing_block method."""
    try:
        DB.flush_db()
    except ConnectionError:
        pytest.fail('Failed to a connect a configuration database (Redis) '
                    'instance!', pytrace=False)
    data_dir = join(dirname(__file__), 'data')
    add_workflow_definitions(join(data_dir, 'workflow_definitions'))
    with open(join(data_dir, 'sbi_config_3.json')) as _file:
        sbi_config = json.load(_file)
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1
    assert pb_ids[0] == 'PB-20181116-sip-001'
    assert isinstance(pb_ids[0], str)

    result = execute_processing_block.apply(args=(pb_ids[0],),
                                            kwargs=dict(log_level='WARNING'))
    assert result.get(timeout=10.0) == 'completed'
