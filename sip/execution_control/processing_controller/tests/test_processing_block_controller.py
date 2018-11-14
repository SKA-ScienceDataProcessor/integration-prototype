# coding=utf-8
"""Unit tests of the Processing Block Controller.

http://docs.celeryproject.org/en/latest/userguide/testing.html
"""

import json
import os
import celery
import time

from celery.app.control import Inspect
from config_db.sbi import DB, SchedulingBlockInstance
from config_db.utils.generate_sbi_configuration import generate_sbi_config
from ..utils.pbc_workflow_definition import add_sbi_workflow_definitions
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
        id='mock_workflow',
        version='1.0.0',
        parameters=dict(setup=dict(duration=20, num_channels=10)))
    workflows_dir = os.path.join(os.path.dirname(__file__), 'data',
                                 'workflows')
    # TODO (NJT) Need to add the workflow definition to the database
    # and read from it and then generate sbi config
    sbi_config = generate_sbi_config(1, workflow_config=workflow_config,
                                     pb_config=dict(type='offline'))
    add_sbi_workflow_definitions(sbi_config, workflows_dir, test_version=1)

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

    print('\nresult =', result)
    # start_time = time.time()
    # _inspect = Inspect(app=APP)
    # while not result.ready():
    #     print('XX', _inspect.active())
    #     print('XX', result.ready(), (time.time() - start_time))
    #     time.sleep(0.5)
