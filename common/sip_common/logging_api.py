# coding: utf-8
"""Logging API for SIP.

This module extends the Python logger for use with SIP modules when writing
log messages.

Basic usage:

.. code-block:: python

    from sip_common.logging_api import log
    log.info('my message')

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import datetime
import getpass
import logging
import logging.handlers
import socket


class SipLogRecord(logging.LogRecord):
    """SIP Log record class.

    Extends the python LoggingRecord adding hostname, username, and
    a python dictionary representation of the log record."""

    def __init__(self, name, level, pathname, lineno, msg, args,
                 exc_info, func=None, sinfo=None):
        """Constructs a SIP logging record.

        A more detailed description of arguments can be found here:
        https://docs.python.org/3.5/library/logging.html#logrecord-objects

        Args:
            name: The name of the logger.
            level: Numeric level of the logging event.
            pathname: The full pathname of the source file where the logging
                      call was made.
            lineno: Line number of the logging call.
            msg: The event description message, possibly a format string.
            args: Variable data to merge into the msg arguement to obtain
                  the event description.
            exc_info: An exception tupple with the current exception info or
                      None
            func: The name of the function from which the logging call was
                  invoked.
            sinfo: A text string representing the stack info in the current
                   thread up to the logging call.
            kwargs:
        """
        logging.LogRecord.__init__(self, name, level, pathname, lineno,
                                   msg, args, exc_info, func, sinfo)
        # Note: Can also access the following variables via the formatter as:
        #   %(hostname)s
        #   %(username)s
        #   %(time)s
        #   %(_raw)s
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
        self.time = datetime.datetime.utcnow().isoformat()
        self._raw = self.__dict__.copy()


class SipLogger(logging.getLoggerClass()):
    """SIP logger class. Overrides the standard logging.Logger class"""

    def makeRecord(self, name, level, pathname, lineno, msg, args, exc_info,
                   func=None, extra=None, sinfo=None):
        """Factory method for creating logging records. Overrides the Logger
         makeRecord() method to make the custom SIP Logging record.

        Args:
            name: The name of the logger.
            level: Numeric level of the logging event.
            pathname: The full pathname of the source file where the logging
                      call was made.
            lineno: Line number of the logging call.
            msg: The event description message, possibly a format string.
            args: Variable data to merge into the msg arguement to obtain
                  the event description.
            exc_info: An exception tupple with the current exception info or
                      None
            func: The name of the function from which the logging call was
                  invoked.
            sinfo: A text string representing the stack info in the current
                   thread up to the logging call.

        Returns:
            logging.LogRecord object
        """
        record = SipLogRecord(name, level, pathname, lineno, msg, args,
                              exc_info, func)
        if extra:
            for key in extra:
                if (key in ['message', 'asctime']) or (key in record.__dict__):
                    raise KeyError('Attempt to overwrite %r in SipLogRecord'
                                   % key)
                record.__dict__[key] = extra[key]
        return record


# Create Logger for use with SIP modules.
from .logging_handlers import ZmqLogHandler
log = SipLogger('sip.log')
# host = os.environ['SIP_HOSTNAME']
host = '127.0.0.1'  # TODO(BM) Needs to be obtained from Resource Discovery.
log.addHandler(ZmqLogHandler.to('all', host=host, level='DEBUG'))
