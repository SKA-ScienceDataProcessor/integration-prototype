# coding: utf-8
""" Test of the heartbeat interface.

The heartbeat interface is used for health checking between the
Master Controller and Slaves.

Run with:
    $ python3 -m unittest -f -v sip.common.test.test_heartbeat
or
    $ python3 -m unittest discover -f -v -p test_heartbeat.py
"""
import logging.handlers
import os
import sys
import time
import unittest
import warnings

import docker

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from sip.common.docker_paas import DockerPaas as Paas


@unittest.skip('Needs fixing.')
class HeartbeatTest(unittest.TestCase):
    """ Test of the Heartbeat interface.

    Makes use of the Docker PaaS interface to run a service and
    then checks for heartbeats.
    """
    @classmethod
    def setUpClass(cls):
        """ Initialise the test class.
        """
        warnings.simplefilter('ignore', ResourceWarning)

        # Get a client to the local docker engine.
        client = docker.from_env()

        # Check if the test is being run from a swarm manager node.
        if not client.info()['Swarm']['ControlAvailable']:
            raise RuntimeError(cls, 'Docker Swarm not availiable.')
            # client.swarm.init()

        # Create a logging server
        # FIXME(BM): This should not be needed to test heartbeat!
        paas = Paas()
        cls.logger = paas.run_service(
            'logging_server',
            'sip',
            [logging.handlers.DEFAULT_TCP_LOGGING_PORT],
            ['python3', 'sip/common/logging_server.py'])

        # Wait for the logging server to come online.
        time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        """ Tear down the test class.
        """
        cls.logger.delete()


    def setUp(self):
        """."""
        # Create a heartbeat sender service
        paas = Paas()
        name = 'heartbeat_sender'
        task = 'sip'
        port = 12345
        cmd = ['python3', 'sip/common/test/mock_heartbeat_sender.py']
        self.sender = paas.run_service(name, task, [port], cmd)
        self.sender_port = port
        time.sleep(1)

    def tearDown(self):
        """."""
        self.sender.delete()

    def test_simple(self):
        """."""
        # Import the heartbeatt Listener class
        # (imports logging_api which needs the logging server to be running)
        from sip.common.heartbeat import Listener

        # Start the heartbeat listener and connect to the sender
        listener = Listener(timeout=2000)
        location = self.sender.location(self.sender_port)
        listener.connect(location[0], location[1])

        msg = listener.listen()
        print('msg = ', msg)

        # # Check that we have received heartbeat messages.
        # recieved_count = 0
        # fail_count = 0
        # while recieved_count < 2:    
        #     msg = listener.listen()
        #     print("msg = '{}'".format(msg))
        #     if msg:
        #         recieved_count += 1
        #         self.assertEqual(msg[0], 'test',
        #                          msg="Name of the sender expected to be 'test'")
        #         self.assertEqual(msg[1], 'ok',
        #                          msg="Heartbeat message expected to be 'ok'")
        #     else:
        #         fail_count += 1
        #         if fail_count > 10:
        #             sender.delete()
        #             self.fail('Failed to receive heartbeat messages.')
        #     time.sleep(0.5)

