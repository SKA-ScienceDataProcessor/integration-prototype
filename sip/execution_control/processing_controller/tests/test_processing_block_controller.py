# coding=utf-8
"""Unit tests of the Processing Block Controller.

http://docs.celeryproject.org/en/latest/userguide/testing.html
"""

import json
from os.path import dirname, join

import celery
from celery.app.control import Inspect

from sip_config_db import ConfigDb
from sip_config_db.scheduling import SchedulingBlockInstance
from .test_utils import add_workflow_definitions
from ..processing_block_controller.release import __version__
from ..processing_block_controller.tasks import APP, \
    execute_processing_block, version

DB = ConfigDb()


def test_pbc_inspect_tasks():
    """."""
    _inspect = Inspect(app=APP)
    print('')
    print('inspect =', _inspect)
    print('scheduled =', _inspect.scheduled())
    print('active =', _inspect.active())
    print('reserved =', _inspect.reserved())
    print('registered tasks =', _inspect.registered_tasks())


def test_pbc_inspect_workers():
    """."""
    print('')
    print('ping workers:', celery.current_app.control.inspect().ping())
    print('stats', json.dumps(celery.current_app.control.inspect().stats(),
                              indent=2))
    # print('workers=', celery.current_app.control.inspect().stats().keys())


def test_pbc_version():
    """."""
    result = version.delay()
    assert result.get(timeout=1) == __version__


def test_pbc_execute_workflow():
    """.
    http://docs.celeryproject.org/en/latest/userguide/tasks.html

    python3 -m pytest -s -v -x --rootdir=. -k
    test_pbc_execute sip/execution_control/processing_controller

    """
    DB.flush_db()
    data_dir = join(dirname(__file__), 'data')
    add_workflow_definitions(join(data_dir, 'workflow_definitions'))
    with open(join(data_dir, 'sbi_config_2.json')) as _file:
        sbi_config = json.load(_file)
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    print('NAME:', execute_processing_block.name)
    state = celery.current_app.events.State()
    print("STATE:", state)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1
    assert pb_ids[0] == 'PB-20181116-sip-001'
    assert isinstance(pb_ids[0], str)

    result = execute_processing_block.delay(pb_ids[0])
    print('result = ', result)
