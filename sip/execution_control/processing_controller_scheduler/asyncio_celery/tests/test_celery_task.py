# -*- coding: utf-8 -*-
"""Tests of starting a Celery (Processing Block Controller) task """
import celery
from mock_processing_block_controller.tasks import execute_processing_block


def test_start_task():
    state = celery.current_app.events.State()
    print(state)
    block_config = dict(id='pb-01')
    execute_processing_block.delay(block_config)
    # execute_processing_block.apply_async((block_config,))
