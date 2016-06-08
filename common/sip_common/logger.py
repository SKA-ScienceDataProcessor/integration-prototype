""" This defines the SIP logging API.

The current implementation uses the standard library logging package.

There is a one-to-one mapping between the log levels defined in the
LMC interface guidelines (see 0026 LMC Design table 1) and the levels
defined by the logging package except that FATAL is mapped to critical
and TRACE maps to 5.
"""
__author__ = 'David Terrett'

import logging

logging.basicConfig(level=logging.NOTSET)
_logger = logging.getLogger(__name__)

def error(msg):
    """ Log an ERROR level message
    """
    _logger.error(msg)

def info(msg):
    """ Log an INFO level message
    """
    _logger.info(msg)

def trace(msg):
    """ Log a TRACE level message
    """
    _logger.log(5, msg)

def warn(msg):
    """ Log a WARN level message
    """
    _logger.warn(msg)
