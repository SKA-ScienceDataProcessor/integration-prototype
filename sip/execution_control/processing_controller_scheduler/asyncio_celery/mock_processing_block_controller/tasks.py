# -*- coding: utf-8 -*-
"""Mock Processing Block Controller Celery task

export CELERY_BROKER=redis://localhost:6379/1
export CELERY_BACKEND=redis://localhost:6379/2
celery -A mock_processing_block_controller.tasks worker -l info
"""
import os
import time

from celery import Celery

BROKER = os.getenv('CELERY_BROKER', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_BACKEND', 'redis://localhost:6379/2')
APP = Celery(broker=BROKER, backend=BACKEND)


@APP.task
def execute_processing_block(config):
    """Execute a processing block.

    Args:
        config (dict): Processing Block Configuration.
    """
    print('Executing Processing block!')
    # print('Executing Processing Block, id = ', config['id'])
    # time.sleep(3.0)
