import subprocess
import time
import unittest
import warnings
import os
import sys
import logging.handlers

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sip.common.docker_paas import DockerPaas as Paas

class HeartbeatTest(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', ResourceWarning)

        # Create a logging server
        paas = Paas()
        self.logger = paas.run_service('logging_server', 'sip',
                logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                ['python3', 'sip/common/logging_server.py'])
        time.sleep(3)

        # Now we can import Listner (which impors logging_api which needs
        # the logging server to be running
        from sip.common.heartbeat import Listener
        sender = 'sip/common/test/heartbeat_test_send.py'
        paas = Paas()
        self.sender = paas.run_service('heartbeat_test_send', 'sip', 12345,
               ['python3', sender] )
        self.listener = Listener(1000)
        self.listener.connect(self.sender.hostname, self.sender.port)

    def testSimple(self):
        time.sleep(5)
        msg = self.listener.listen()
        self.assertEqual(msg[0], 'test')
        self.sender.delete()
        self.logger.delete()

if __name__ == '__main__':
    unittest.main()
