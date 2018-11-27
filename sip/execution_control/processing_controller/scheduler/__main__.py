# -*- coding: utf-8 -*-
"""Processing Controller Scheduler application main."""
from sip_logging import init_logger
from sip_logging.sip_logging import disable_logger
from .log import LOG
from .release import __service_name__
from .scheduler import ProcessingBlockScheduler

if __name__ == '__main__':
    init_logger(show_log_origin=False, show_thread=True, p3_mode=False)
    disable_logger('sip.ec.config_db')
    LOG.info('Starting %s', __service_name__)
    ProcessingBlockScheduler().start()
