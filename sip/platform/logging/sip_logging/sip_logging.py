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
import sys
import logging
import os
import datetime


class SIPFormatter(logging.Formatter):
    """Custom log formatter class to add microsecond precision timestamps."""

    converter = datetime.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        """Format the log timestamp."""
        _created = self.converter(record.created)
        if datefmt:
            time_string = _created.strftime(datefmt)
        else:
            time_string = _created.strftime("%Y-%m-%d %H:%M:%S")
            time_string = "%s,%03d" % (time_string, record.msecs)
        return time_string


def init_logger(log_level=None):
    """Initialise the SIP logger.

    Attaches a stdout stream handler to the 'sip' logger. This will
    apply to all logger objects with a name prefixed by 'sip.'

    This function respects the 'SIP_LOG_LEVEL' environment variable to
    set the logging level.

    Args:
        log_level (str or int, optional): Logging level for the SIP logger.

    """
    log = logging.getLogger('sip')
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = os.getenv('SIP_LOG_FORMAT', '%(asctime)s | %(name)s | '
                                      '%(levelname)-7s | %(message)s')
    formatter = SIPFormatter(fmt, datefmt='%Y-%m-%dT%H:%M:%S.%f')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    if log_level:
        log.setLevel(log_level)
    else:
        log.setLevel(os.getenv('SIP_LOG_LEVEL', 'DEBUG'))
