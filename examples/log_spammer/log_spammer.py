# coding: utf-8
"""Dummy app to spam a log messages for testing the logging system."""
import argparse
import logging
import time

from sip_logging import init_logger


def main(sleep_length=0.1):
    """Log to stdout using python logging in a while loop"""
    log = logging.getLogger('sip.examples.log_spammer')

    log.info('Starting to spam log messages every %fs', sleep_length)
    counter = 0
    try:
        while True:
            log.info('Hello %i', counter)
            counter += 1
            time.sleep(sleep_length)
    except KeyboardInterrupt:
        log.info('Exiting...')


if __name__ == '__main__':
    init_logger()
    PARSER = argparse.ArgumentParser(description='Spam stdout with Python '
                                                 'logging.')
    PARSER.add_argument('sleep_length', type=float,
                        help='number of seconds to sleep between messages.')

    args = PARSER.parse_args()
    main(args.sleep_length)
