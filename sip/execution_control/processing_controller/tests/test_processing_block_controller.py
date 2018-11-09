# coding=utf-8
"""Unit tests of the Processing Block Controller.

http://docs.celeryproject.org/en/latest/userguide/testing.html
"""

import json

import celery
from celery.app.control import Inspect
from config_db.sbi import DB, SchedulingBlockInstance
from config_db.utils.generate_sbi_configuration import generate_sbi_config
from config_db.tests.workflow_test_utils import \
    add_test_sbi_workflow_definitions

from ..processing_block_controller.tasks import APP, execute_processing_block


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


def test_pbc_execute():
    """.

    http://docs.celeryproject.org/en/latest/userguide/tasks.html
    """
    DB.flush_db()
    workflow_config = dict(
        id='test_workflow',
        version='4.0.0',
        parameters=dict(setup=dict(duration=5, num_channels=10)))
    sbi_config = generate_sbi_config(1, workflow_config=workflow_config,
                                     pb_config=dict(type='offline'))
    add_test_sbi_workflow_definitions(sbi_config, test_version=4)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    print('NAME=', execute_processing_block.name)
    state = celery.current_app.events.State()
    print("STATE", state)

    pb_ids = sbi.processing_block_ids
    print('PB IDS', pb_ids)
    assert len(pb_ids) == 1
    print('pb_ids[0]', pb_ids[0])
    print('type', type(pb_ids[0]))

    result = execute_processing_block.apply_async((pb_ids[0], ))

    # print('\nresult =', result)
    # start_time = time.time()
    # _inspect = Inspect(app=APP)
    # while not result.ready():
    #     print('XX', _inspect.active())
    #     print('XX', result.ready(), (time.time() - start_time))
    #     time.sleep(0.5)
