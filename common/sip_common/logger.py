import logging, logging.handlers
import os
import zmq
from zmq.log.handlers import PUBHandler

""" This defines the SIP logging API.

The current implementation uses the standard library logging package.

There is a one-to-one mapping between the log levels defined in the
LMC interface guidelines (see 0026 LMC Design table 1) and the levels
defined by the logging package except that FATAL is mapped to critical
and TRACE maps to 10 (DEBUG).

It uses zmq.PUB to publish the logs to the logging_server which subscribes 
to all publishers; the name of the host where to send logs is taken from 
the environment variable SIP_HOSTNAME, defined in the beginning of 
$SIP_HOME/master/bin/master script.

The TCP port used is logging.handlers.DEFAULT_TCP_LOGGING_PORT, which is 9020.
"""
__author__ = 'David Terrett, Vlad Stolyarov'


_logger = logging.getLogger(__name__)
_logger.setLevel(1)

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
pub.connect('tcp://%s:%i' % (os.environ['SIP_HOSTNAME'], port))

handler = PUBHandler(pub)
_logger.addHandler(handler)


def debug(msg):
    """ Log an DEBUG level message
    """
    _logger.debug(msg)


def info(msg):
    """ Log an INFO level message
    """
    _logger.info(msg)


def warn(msg):
    """ Log a WARN level message
    """
    _logger.warn(msg)


def error(msg):
    """ Log an ERROR level message
    """
    _logger.error(msg)


def fatal(msg):
    """ Log a FATAL level message
    """
    _logger.critical(msg)

