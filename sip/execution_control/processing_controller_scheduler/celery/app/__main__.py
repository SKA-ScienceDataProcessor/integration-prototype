# -*- coding: utf-8 -*-
"""Processing Controller Scheduler application main."""
import logging
import os

from .scheduler_async import ProcessingBlockScheduler


def _init_logger():
    """Initialise the logger."""
    _log = logging.getLogger('sip')
    _handler = logging.StreamHandler()
    fmt = os.getenv('SIP_LOG_FORMAT', '%(asctime)s.%(msecs)03d | '
                    '%(name)s | %(levelname)-7s | %(message)s')
    _handler.setFormatter(logging.Formatter(fmt, '%Y-%m-%d %H:%M:%S'))
    _log.addHandler(_handler)
    _log.setLevel(os.getenv('SIP_PC_LOG_LEVEL', 'DEBUG'))
    return _log


if __name__ == '__main__':
    LOG = _init_logger()
    LOG.info("Starting Processing Controller!")
    ProcessingBlockScheduler().run()
