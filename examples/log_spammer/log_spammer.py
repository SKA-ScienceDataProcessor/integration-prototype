# coding: utf-8
"""Dummy app to spam a log messages for testing the logging system."""
import logging
import sys
import time


def main():
    """Log to stdout using python logging in a while loop"""
    log = logging.getLogger('SIP.examples.log_spammer')
    log.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s '
                                  '- %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    counter = 0
    try:
        while True:
            log.info('Hello %i', counter)
            log.debug('Hello again %i', counter)
            counter += 1
            time.sleep(0.1)
    except KeyboardInterrupt:
        log.info('Exiting...')


if __name__ == '__main__':
    main()
