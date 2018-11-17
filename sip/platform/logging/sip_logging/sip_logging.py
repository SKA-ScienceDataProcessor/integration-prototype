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


def init_logger(log_level=None, p3_mode: bool = True,
                show_thread: bool = False, propagate: bool = False):
    """Initialise the SIP logger.

    Attaches a stdout stream handler to the 'sip' logger. This will
    apply to all logger objects with a name prefixed by 'sip.'

    This function respects the 'SIP_LOG_LEVEL' environment variable to
    set the logging level.

    Args:
        log_level (str or int, optional): Logging level for the SIP logger.
        p3_mode (bool, optional): Print logging statements in a format that
                                  P3 can support.
        show_thread (bool, optional): Display the thread in the log message.
        propagate (bool, optional): Propagate settings to parent loggers.

    """
    log = logging.getLogger('sip')
    log.propagate = propagate

    # Remove existing handlers (to avoid duplicate messages if the log is
    #                           initialised twice)
    for handler in log.handlers:
        log.removeHandler(handler)
    if p3_mode:
        if show_thread:
            # _format = '%(asctime)s.%(msecs)03dZ | %(name)s ' \
            #           '| %(levelname)-7s | %(threadName)-22s | %(message)s'
            _format = '%(asctime)s - %(name)s ' \
                      '- %(levelname)s - %(threadName)-22s - %(message)s'
        else:
            # _format = '%(asctime)s.%(msecs)03dZ | %(name)s ' \
            #           '| %(levelname)-7s | %(message)s'
            _format = '%(asctime)s - %(name)s ' \
                      '- %(levelname)s - %(message)s'
        formatter = logging.Formatter(_format)
        formatter.converter = time.gmtime
    else:
        if show_thread:
            _format = '%(asctime)s | %(name)s | %(levelname)-7s | ' \
                      '%(threadName)-22s | %(message)s'
        else:
            _format = '%(asctime)s | %(name)s | %(levelname)-7s | %(message)s'
        formatter = SIPFormatter(_format, datefmt='%Y-%m-%dT%H:%M:%S.%fZ')

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    if log_level:
        log.setLevel(log_level)
    else:
        log.setLevel(os.getenv('SIP_LOG_LEVEL', 'DEBUG'))
