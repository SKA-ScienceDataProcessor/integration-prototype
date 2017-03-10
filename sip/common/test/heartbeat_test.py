import subprocess
import time
import unittest
import os
import sys

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sip.common.heartbeat import Listener


class HeartbeatTest(unittest.TestCase):
    def setUp(self):
        proc = os.path.join(os.path.dirname(__file__),'heartbeat_test_send.py')
        self.pid = subprocess.Popen(proc)
        self.listener = Listener(1000)
        self.listener.connect('localhost', '12345')

    def testSimple(self):
        time.sleep(2)
        msg = self.listener.listen()
        self.assertEqual(msg[0], 'test')
        self.pid.kill()

if __name__ == '__main__':
    unittest.main()
