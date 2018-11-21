# -*- coding: utf-8 -*-
"""Processing Controller Scheduler application main."""
from sip_logging import init_logger

from .scheduler import ProcessingBlockScheduler
from .log import LOG
from .release import __service_name__

if __name__ == '__main__':
    init_logger()
    LOG.info('Starting %s', __service_name__)
    ProcessingBlockScheduler().start()
