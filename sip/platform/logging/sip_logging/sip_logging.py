# coding: utf-8
"""Utility module for standardising python logging throughout SIP.

Usage:

```python
import logging
from sip_logging import init_logger

def foo():
    log = logging.getLogger('sip.foo')
    log.info('Hello')

if __name__ == '__main__':
     init_logger()
```

"""
import time
import sys
import logging
import os
import datetime


class SIPFormatter(logging.Formatter):
    """Custom log formatter class to add microsecond precision timestamps."""

    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        """Format the log timestamp."""
        _seconds_fraction = record.created - int(record.created)
        _datetime_utc = time.mktime(time.gmtime(record.created))
        _datetime_utc += _seconds_fraction
        _created = self.converter(_datetime_utc)

        if datefmt:
            time_string = _created.strftime(datefmt)
        else:
            time_string = _created.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            time_string = "%s,%03d" % (time_string, record.msecs)
        return time_string


def init_logger(logger_name='sip', log_level=None, p3_mode: bool = True,
                show_thread: bool = False, propagate: bool = False,
                show_log_origin=False):
    """Initialise the SIP logger.

    Attaches a stdout stream handler to the 'sip' logger. This will
    apply to all logger objects with a name prefixed by 'sip.'

    This function respects the 'SIP_LOG_LEVEL' environment variable to
    set the logging level.

    Args:
        logger_name (str, optional): Name of the logger object.
        log_level (str or int, optional): Logging level for the SIP logger.
        p3_mode (bool, optional): Print logging statements in a format that
            P3 can support.
        show_thread (bool, optional): Display the thread in the log message.
        propagate (bool, optional): Propagate settings to parent loggers.
        show_log_origin (boo, optional): If true show the origin
            (file, line no.) of log messages.

    """
    log = logging.getLogger(logger_name)
    log.propagate = propagate

    # Remove existing handlers (avoids duplicate messages)
    for handler in log.handlers:
        log.removeHandler(handler)

    _debug = '%(filename)s:%(lineno)d | ' if show_log_origin else ''

    # P3 mode is intended to work with the fluentd configuration on P3.
    # This has ms timestamp precision and uses '-' as a delimiter
    # between statements in the log file.
    if p3_mode:
        _prefix = '%(asctime)s - %(name)s - %(levelname)s'
        if show_thread:
            _format = '{} - %(threadName)s - {}%(message)s'\
                .format(_prefix, _debug)
        else:
            _format = '{} - {}%(message)s'.format(_prefix, _debug)
        formatter = logging.Formatter(_format)
        formatter.converter = time.gmtime
    # If not in P3 mode, the timestamp will be us precision and use '|'
    # as a separator.
    else:
        _prefix = '%(asctime)s | %(name)s | %(levelname)s'
        if show_thread:
            _format = '{} | %(threadName)s | {}%(message)s'\
                .format(_prefix, _debug)
        else:
            _format = '{} | {}%(message)s'.format(_prefix, _debug)
        formatter = SIPFormatter(_format, datefmt='%Y-%m-%dT%H:%M:%S.%fZ')

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # Set the logging level.
    if log_level:
        log.setLevel(log_level)
    else:
        log.setLevel(os.getenv('SIP_LOG_LEVEL', 'DEBUG'))


def disable_logger(logger_name: str, propagate: bool = False):
    """Disable output for the logger of the specified name."""
    log = logging.getLogger(logger_name)
    log.propagate = propagate
    for handler in log.handlers:
        log.removeHandler(handler)


def set_log_level(logger_name: str, log_level: str, propagate: bool = False):
    """Set the log level of the specified logger."""
    log = logging.getLogger(logger_name)
    log.propagate = propagate
    log.setLevel(log_level)
