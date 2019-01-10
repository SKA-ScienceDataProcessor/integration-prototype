# SKA SDP SIP logging module

Provides a function for initialising the SIP logger. This uses a custom
logging formatter class which prints log messages with microsecond timestamps. 

Typical usage:

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

When initialising the SIP logger, optional arguments to the `init_logger`
function provide some degree of customisation such as displaying the 
origin of log messages, displaying the thread id from which the log originates,
setting the logging level, and some options which control the output format
needed for running with the fluentd logging driver on the P3-alaSKA system.

In addition to these options, the logging level can be set by setting the 
environment variable `SIP_LOG_LEVEL` to a valid Python logging level specifier.
