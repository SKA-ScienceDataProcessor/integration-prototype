# -*- coding: utf-8 -*-
"""Processing Block Controller (Celery worker)"""
import os
from celery import Celery


APP = Celery('tasks', broker=os.getenv('CELERY_BROKER'))


@APP.task
def execute_processing_block(workflow):
    """Execute a processing block.

    Args:
        workflow (dict): Workflow description.
    """
    print("Celery Hello World!")
    pass
