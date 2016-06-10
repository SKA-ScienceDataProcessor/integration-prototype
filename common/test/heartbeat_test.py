from multiprocessing import Process
import subprocess
import time
import unittest

from sip_common.heartbeat import Listener

class HeartbeatTest(unittest.TestCase):
    def setUp(self):
        self.pid = subprocess.Popen('./heartbeat_test_send.py')
        self.listener = Listener(1000)
        self.listener.connect('localhost', '12345')

    def testSimple(self):
        time.sleep(2)
        msg = self.listener.listen()
        self.assertEqual(msg[0], 'test')
        self.pid.kill()

if __name__ == '__main__':
    unittest.main()
