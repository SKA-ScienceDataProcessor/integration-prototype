#!/usr/bin/env python3

# Helper script for the heartbeat test.

import time
import os
import sys

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from sip.common.heartbeat import Sender

if __name__ == '__main__':
    sender = Sender('test', '12345')
    for i in range(0, 10):
        sender.send('ok')
        time.sleep(1)
