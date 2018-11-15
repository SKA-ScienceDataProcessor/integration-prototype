# coding: utf-8
"""Dummy app to spam a log messages for testing the logging system."""
import argparse
import logging
import time

import _version
from sip_logging import init_logger, __version__


def main(sleep_length=0.1):
    """Log to stdout using python logging in a while loop"""
    log = logging.getLogger('sip.examples.log_spammer')

    log.info('Starting to spam log messages every %fs', sleep_length)
    counter = 0
    try:
        while True:
            log.info('Hello %06i (log_spammer: %s, sip logging: %s)',
                     counter, _version.__version__, __version__)
            counter += 1
            time.sleep(sleep_length)
    except KeyboardInterrupt:
        log.info('Exiting...')


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Spam stdout with Python '
                                                 'logging.')
    PARSER.add_argument('sleep_length', type=float,
                        help='number of seconds to sleep between messages.')
    PARSER.add_argument('--timestamp_us', required=False, action='store_true',
                        help='Use microsecond timestamps.')
    args = PARSER.parse_args()

    P3_MODE = False if args.timestamp_us else True
    print(args.timestamp_us, P3_MODE)
    init_logger(p3_mode=P3_MODE)

    main(args.sleep_length)
