# -*- coding: utf-8 -*-
"""Processing Controller Scheduler application main."""
from sip_logging import init_logger

from .scheduler import ProcessingBlockScheduler

if __name__ == '__main__':
    init_logger()
    ProcessingBlockScheduler().start()
