""" This defines the SIP logging API.

The current implementation uses the standard library logging package.

There is a one-to-one mapping between the log levels defined in the
LMC interface guidelines (see 0026 LMC Design table 1) and the levels
defined by the logging package except that FATAL is mapped to critical
and TRACE maps to 5.

It uses logging.handlers.SocketHandler() to communicate with logging_server,
the name of the host to send logs is taken from the environment variable
SIP_HOSTNAME, defined in the beginning of $SIP_HOME/master/bin/master script .
The logging.handlers.DEFAULT_TCP_LOGGING_PORT is 9020 .

"""
__author__ = 'David Terrett, Vlad Stolyarov'

import logging, logging.handlers
import os

_logger = logging.getLogger(__name__)
_logger.setLevel(1)

socketHandler = logging.handlers.SocketHandler(os.environ['SIP_HOSTNAME'],
                    logging.handlers.DEFAULT_TCP_LOGGING_PORT)
# don't bother with a formatter, since a socket handler sends the event as
# an unformatted pickle
_logger.addHandler(socketHandler)

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
