#!/usr/bin/python3

""" Skeleton slave controller for use in a Docker container

All it does is send heartbeat messages

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

import os
import signal
import sys
import time

sys.path.append('/home/sdp/lib/python')
import heartbeat
import logger

def _sig_handler(signum, frame):
    sys.exit(0)

def run():
    name = os.environ['MY_NAME']
    logger.info('Slave controller "' + name + '" starting')

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # Create a heartbeat sender
    heartbeat_sender = heartbeat.Sender(name)
    while True:
        heartbeat_sender.send()
        time.sleep(1)

if __name__ == '__main__':
    run()
