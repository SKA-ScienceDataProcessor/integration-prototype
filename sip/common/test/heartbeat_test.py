# coding: utf-8
"""Test of the heartbeat interface.

Run with:
    $ python3 -m unittest sip.common.test.test_heartbeat
"""
import logging.handlers
import os
import sys
import time
import unittest
import warnings

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sip.common.docker_paas import DockerPaas as Paas


@unittest.skip("Need to skip if docker swarm does not exist.")
class HeartbeatTest(unittest.TestCase):
    """Test of the Heartbeat interface.

    Makes use of the Docker PaaS interface to run a service and
    then checks for heartbeats.
    """

    def setUp(self):
        """."""
        warnings.simplefilter('ignore', ResourceWarning)

        # Create a logging server
        paas = Paas()
        self.logger = paas.run_service(
            'logging_server', 'sip',
            [logging.handlers.DEFAULT_TCP_LOGGING_PORT],
            ['python3', 'sip/common/logging_server.py'])
        time.sleep(3)

        # Now we can import Listener (which imports logging_api which needs
        # the logging server to be running
        from sip.common.heartbeat import Listener
        sender = 'sip/common/test/mock_heartbeat_sender.py'
        paas = Paas()
        self.sender = paas.run_service('heartbeat_sender', 'sip', [12345],
                                       ['python3', sender])
        self.listener = Listener(2000)
        location = self.sender.location(12345)
        self.listener.connect(location[0], location[1])

    def test_simple(self):
        """."""
        time.sleep(5)
        msg = self.listener.listen()
        self.assertEqual(msg[0], 'test')
        self.sender.delete()
        self.logger.delete()

if __name__ == '__main__':
    unittest.main()
