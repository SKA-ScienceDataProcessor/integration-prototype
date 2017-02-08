#!/usr/bin/env python3

# Helper script for the heartbeat test.

import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sip_common.heartbeat import Sender

if __name__ == '__main__':
    sender = Sender('test', '12345')
    for i in range(0, 10):
        sender.send('ok')
        time.sleep(1)
