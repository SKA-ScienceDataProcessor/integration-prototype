# -*- coding: utf-8 -*-
""" Test of docker platform as a service

Run with:
    $ python3 -m unittest sip.common.tests.test_paas_docker
or:
    $ python3 -m unittest discover -f -v -p test_paas_docker.py

.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""

import socket
import time
import unittest
import warnings

import rpyc
import docker

from sip.common.docker_paas import DockerPaas as Paas
from sip.common.paas import TaskStatus


REPEAT_COUNT = 1  # Number of times to run each test


def repeat(times):
    """ Decorator that can be used to repeat a test.
    """
    # pylint: disable=missing-docstring
    def repeat_helper(method):
        def call_helper(*args):
            for _ in range(0, times):
                method(*args)
            call_helper.__doc__ = "Hello"
        return call_helper
    return repeat_helper


class TestDocker(unittest.TestCase):
    """ Tests of the Docker Platform as a service interface.
    """

    @classmethod
    def setUpClass(cls):
        """ Initialise the test class.
        """
        # The docker python API keeps the socket to the docker engine open so
        # we need to suppress the resource warning from unittest
        warnings.simplefilter('ignore', ResourceWarning)

        client = docker.from_env()

        # Store state of docker swarm so it can be recovered after the test
        if not client.info()['Swarm']['ControlAvailable']:
            cls.swarm_mode_enabled = False
        else:
            cls.swarm_mode_enabled = True

    @classmethod
    def tearDownClass(cls):
        """ Tear down the test class.
        """
        client = docker.from_env()
        if cls.swarm_mode_enabled:
            client.swarm.init()

    def setUp(self):
        """ Prepare the test fixture
        """
        client = docker.from_env()
        if not client.info()['Swarm']['ControlAvailable']:
            client.swarm.init()

    def tearDown(self):
        """ Tear down the test fixture
        """
        client = docker.from_env()
        if client.info()['Swarm']['ControlAvailable']:
            client.swarm.leave(force=True)

    @repeat(REPEAT_COUNT)
    def test_run_task(self):
        """ Test normal execution of a Docker Swarm 'task'
        """
        # Start the task
        service_name = 'test_task'
        image = 'sip'
        timeout = 3
        exit_code = 0
        cmd = [
            'python3',
            'sip/common/tests/mock_task.py',
            str(timeout),
            str(exit_code)
        ]
        descriptor = Paas().run_task(name=service_name, task=image, ports=[],
                                     cmd_args=cmd)

        # It should be running
        self._poll_for(TaskStatus.RUNNING, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.RUNNING)

        # Wait for the task to finish running.
        start_time = time.time()
        while descriptor.status() == TaskStatus.RUNNING:
            time.sleep(0.05)
            if (time.time() - start_time) > int(timeout) * 2:
                self.fail('Unexpected timeout reached.')

        # The task should now have exited.
        self._poll_for(TaskStatus.EXITED, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.EXITED)

        # Delete the service.
        descriptor.delete()
        self._poll_for(TaskStatus.UNKNOWN, descriptor)

        # Check that the task no longer exists.
        self._poll_for(TaskStatus.UNKNOWN, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.UNKNOWN)

    # def testService(self):
    #     """ Test normal execution of service
    #     """
    #     # Start the task
    #     time.sleep(10)
    #     t = paas.run_service('test_service', 'sip', [9999],
    #                          ['python3', 'sip/common/tests/mock_service.py',
    #                           '9999'])
    #
    #     # It should be running
    #     self._poll_for(TaskStatus.RUNNING, t)
    #     self.assertEqual(t.status(), TaskStatus.RUNNING)
    #
    #     # Check that we can talk to it
    #     (hostname, port) = t.location(9999)
    #     conn = rpyc.connect(host=hostname, port=port)
    #     conn.root.hello()
    #
    #     # Stop the task
    #     t.delete()
    #     self._poll_for(TaskStatus.UNKNOWN, t)
    #     self.assertEqual(t.status(), TaskStatus.UNKNOWN)
    #
    # def testStop(self):
    #     """ Test of stopping a task
    #     """
    #     time.sleep(10)
    #     t = paas.run_task('test_stop', 'sip', [],
    #                       ['python3', 'sip/common/tests/mock_task.py', '30',
    #                        '0'])
    #
    #     self._poll_for(TaskStatus.RUNNING, t)
    #     self.assertEqual(t.status(), TaskStatus.RUNNING)
    #     t.delete()
    #     self._poll_for(TaskStatus.UNKNOWN, t)
    #     self.assertEqual(t.status(), TaskStatus.UNKNOWN)
    #
    # # def testEndInError(self):
    # #    """ Test of task that exits with an error status
    # #    """
    # #    t = paas.run_task('test_stop', 'sip', [],
    # #            ['python3', 'sip/common/tests/mock_task.py', '3', '1'])
    # #    time.sleep(10)
    # #    self.assertEqual(t.status(), TaskStatus.ERROR)
    # #    t.delete()
    # #    time.sleep(5)
    #
    # def testDuplicateService(self):
    #     """ Test trying to start a service twice with the same name
    #     """
    #     # Start the task
    #     time.sleep(10)
    #     t1 = paas.run_service('test_dup', 'sip', [9999],
    #                           ['python3', 'sip/common/tests/mock_service.py',
    #                            '9999'])
    #
    #     t2 = paas.run_service('test_dup', 'sip', [9999],
    #                           ['python3', 'sip/common/tests/mock_service.py',
    #                            '9999'])
    #
    #     self.assertEqual(t1.ident, t2.ident)
    #
    #     t1.delete()
    #     self._poll_for(TaskStatus.UNKNOWN, t1)
    #
    # def testDuplicateTask(self):
    #     """ Test trying to start a task twice with the same name
    #     """
    #     # Start the task
    #     time.sleep(10)
    #     t1 = paas.run_task('test_task_2', 'sip', [],
    #                        ['python3', 'sip/common/tests/mock_service.py',
    #                         '9999'])
    #
    #     # Try another
    #     t2 = paas.run_task('test_task_2', 'sip', [],
    #                        ['python3', 'sip/common/tests/mock_service.py',
    #                         '9999'])
    #
    #     self.assertNotEqual(t1.ident, t2.ident)
    #     t2.delete()
    #     self._poll_for(TaskStatus.UNKNOWN, t2)
    #
    # def testFind(self):
    #     """ Test finding a task
    #     """
    #     # Start the task
    #     time.sleep(10)
    #     t1 = paas.run_task('test_find', 'sip', [],
    #                        ['python3', 'sip/common/tests/mock_task.py', '0',
    #                         '0'])
    #
    #     # Find it
    #     t2 = paas.find_task('test_find')
    #
    #     self.assertEqual(t1.ident, t2.ident)
    #     t2.delete()
    #     self._poll_for(TaskStatus.UNKNOWN, t2)

    def _poll_for(self, status, task_descriptor, timeout=20):
        """ Poll the task descriptor for a status until timeout is reached.

        Args:
            status: Task status to poll for.
            task_descriptor: Task descriptor object
            timeout (float): Timeout in seconds after which polling stops.
        """
        start_time = time.time()
        while not task_descriptor.status() == status:
            if (time.time() - start_time) >= timeout:
                task_descriptor.delete()
                self.fail('Task status not {} after {} s (cleaning up task)'.
                          format(status, timeout))
            time.sleep(0.2)
