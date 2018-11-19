# SIP logging module

Provides a function for initialising the SIP logger. This uses a custom
logging formatter class which prints log messages with microsecond timestamps. 

Usage:

```python
import logging
from sip_logging import init_logger


def foo():
    log = logging.getLogger('sip.foo')
    log.info('hello world!')


if __name__ == '__main__':
    init_logger()
    foo()
```
