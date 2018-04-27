# -*- coding: utf-8 -*-
"""Processing Controller Scheduler main function"""

import logging
from .scheduler import ProcessingBlockScheduler


def _init_logger():
    """Initialise the logger"""
    _log = logging.getLogger('sip.processing_block_scheduler')
    _log.setLevel(logging.DEBUG)
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - '
                                            '%(name)s - '
                                            '%(levelname).1s - '
                                            '%(message)s',
                                            '%Y-%m-%d %H:%M:%S'))
    _log.addHandler(_handler)
    return _log


if __name__ == '__main__':
    log = _init_logger()
    log.info("Starting Processing Controller!")
    ProcessingBlockScheduler().run()

