# coding=utf-8
"""Unit tests of the Processing Block Controller.

http://docs.celeryproject.org/en/latest/userguide/testing.html
"""
import time
# import logging

import json  # pylint: disable=unused-import
import celery  # pylint: disable=unused-import

from celery.app.control import Inspect

from ..processing_block_controller.tasks import execute_processing_block
from ..processing_block_controller.tasks import APP


def test_inspect_tasks():
    """."""
    _inspect = Inspect(app=APP)
    print('')
    print('inspect =', _inspect)
    print('scheduled =', _inspect.scheduled())
    print('active =', _inspect.active())
    print('reserved =', _inspect.reserved())
    print('registered tasks =', _inspect.registered_tasks())


def test_inspect_workers():
    """."""
    print('')
    print('ping workers:', celery.current_app.control.inspect().ping())
    print('stats', json.dumps(celery.current_app.control.inspect().stats(),
                              indent=2))
    # print('workers=', celery.current_app.control.inspect().stats().keys())


def test_execute_processing_block():
    """.

    http://docs.celeryproject.org/en/latest/userguide/tasks.html
    """
    print('NAME=', execute_processing_block.name)
    state = celery.current_app.events.State()
    print("STATE", state)
    config = dict(id='pb-01', timeout=0.1)
    print(config)
    result = execute_processing_block.apply_async((config,))
    print('\nresult =', result)
    start_time = time.time()
    _inspect = Inspect(app=APP)
    while not result.ready():
        print('XX', _inspect.active())
        print('XX', result.ready(), (time.time() - start_time))
        time.sleep(0.5)
