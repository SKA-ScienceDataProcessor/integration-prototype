#!/usr/bin/python3

""" Skelton slave controller for use in a Docker container

All it does is sleep for a day.

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

import signal
import sys
import time

sys.path.append('/home/sdp/lib/python')
import logger

def _sig_handler(signum, frame):
    sys.exit(0)

def run():
    logger.info('Slave controller starting')
    signal.signal(signal.SIGTERM, _sig_handler)
    time.sleep(86400)

if __name__ == '__main__':
    run()
