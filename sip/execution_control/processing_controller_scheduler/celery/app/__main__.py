# -*- coding: utf-8 -*-
"""Processing Controller Scheduler application main."""
import logging
from .scheduler import ProcessingBlockScheduler


def _init_logger():
    """Initialise the logger."""
    _log = logging.getLogger('sip.ec.scheduler')
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
    LOG = _init_logger()
    LOG.info("Starting Processing Controller!")
    ProcessingBlockScheduler().run()
