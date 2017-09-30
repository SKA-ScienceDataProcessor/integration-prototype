#!/usr/bin/env python3
""" Helper script for the heartbeat test.

This script is used to create a mock service which just sends heartbeat.
"""
import time
import os
import sys

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from sip.common.heartbeat import Sender


if __name__ == '__main__':
    print('Starting sender.')
    SENDER = Sender('test', '12345')
    COUNTER = 0
    try:
        while True:
            print('Sending message %i' % COUNTER, flush=True)
            SENDER.send('ok')
            COUNTER += 1
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('Interrupted!')
