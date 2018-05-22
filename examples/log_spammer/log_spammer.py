# coding: utf-8
"""Dummy app to spam a bunch of logs"""
import logging
import random
import socket
import sys
import time


def main():
    """."""
    log = logging.getLogger('SIP.examples.log_spammer')
    log.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stream=sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s '
                                  '- %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    host_name = socket.gethostname()
    log.info('Starting Log Spammer! ...')
    log.info('hostname = %s', host_name)
    log.info('address  = %s', socket.gethostbyname(host_name))

    counter = 0
    start_time = time.time()
    try:
        while True:
            elapsed = time.time() - start_time
            log.info('hello from %s. (elapsed = %.1f s, counter = %i)',
                     host_name, elapsed, counter)
            log.debug('this is a debug message from %s', host_name)
            counter += 1
            time.sleep(random.uniform(0.001, 0.02))
    except KeyboardInterrupt:
        log.info('Exiting...')


if __name__ == '__main__':
    main()
