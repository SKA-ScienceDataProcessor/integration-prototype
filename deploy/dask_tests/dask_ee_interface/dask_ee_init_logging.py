# -*- coding: utf-8 -*-
"""Script to test how to initialise logging on Dask."""
import logging
import sys

from dask.distributed import Client


def check_loggers():
    """Check Python loggers."""
    print('*** ROOT, no. handlers = %i' % len(logging.getLogger().handlers))
    for key, logger in logging.Logger.manager.loggerDict.items():
        try:
            print('*** key=%s, no. handlers = %i' %
                  (key, len(logger.handlers)))
        except AttributeError:
            pass


def init_logging():
    """Initialise the SIP Python logger."""
    log = logging.getLogger('SIP')
    # If no handlers have been assigned, attach a StreamHandler.
    if not log.handlers:
        log.propagate = True  # Propagate to all SIP.* loggers
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)-15s [%(name)s] %(message)s'))
        log.addHandler(handler)
        log.setLevel('DEBUG')
        log.info('*' * 80)
        log.info('Initialised SIP logger')
    else:
        log.info('*' * 80)
        log.info('SIP logger already initialised')

    # log.info('*' * 80)
    # check_loggers()
    # log.info('*' * 80)


def main():
    """Initialise logging on the dask workers and scheduler."""
    client = Client('localhost:8786')
    client.run(init_logging)
    client.run_on_scheduler(init_logging)


if __name__ == '__main__':
    main()
