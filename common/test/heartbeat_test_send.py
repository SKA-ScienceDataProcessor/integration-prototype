#!/usr/bin/python3

# Helper script for the heartbeat test.

import time

from sip_common.heartbeat import Sender

sender = Sender('test', '12345')
for i in range(0, 10):
    sender.send('ok')
    time.sleep(1)

