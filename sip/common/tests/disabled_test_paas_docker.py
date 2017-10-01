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


REPEAT_COUNT = 3  # Number of times to run each test


def repeat(times):
    """ Decorator that can be used to repeat a test.
    """
    # pylint: disable=missing-docstring
    def repeat_helper(method):
        def call_helper(*args):
            for i in range(times):
                # If running more than once reinitialise the swarm between
                # tests as this won't be done by setUp / tearDown.
                if i > 0:
                    client = docker.from_env()
                    client.swarm.leave(force=True)
                    client.networks.prune()
                    client.swarm.init()
                method(*args)
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
        client.networks.prune()
        if not client.info()['Swarm']['ControlAvailable']:
            client.swarm.init()

    def tearDown(self):
        """ Tear down the test fixture
        """
        client = docker.from_env()
        if client.info()['Swarm']['ControlAvailable']:
            client.swarm.leave(force=True)
            client.networks.prune()

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

    @repeat(REPEAT_COUNT)
    def test_run_services(self):
        """ Test normal execution of service
        """
        # Start the task
        service_name = 'mock_service'
        service_port = 9999
        cmd = [
            'python3',
            'sip/common/tests/mock_service.py',
            str(service_port)
        ]
        descriptor = Paas().run_service(service_name, 'sip', [service_port],
                                        cmd)

        # It should be running
        self._poll_for(TaskStatus.RUNNING, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.RUNNING)

        # Check that we can connect to the service's RPyC interface.
        hostname, port = descriptor.location(service_port)
        try:
            conn = rpyc.connect(host=hostname, port=port)
        except socket.timeout:
            descriptor.delete()
            self._poll_for(TaskStatus.UNKNOWN, descriptor)
            self.fail('Not able to connect to the services RPyC endpoint')

        # Try to talk to the service over RPYC
        self.assertTrue(conn.root.hello().startswith('hello from '))

        # Stop the task
        descriptor.delete()
        self._poll_for(TaskStatus.UNKNOWN, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.UNKNOWN)

    @repeat(REPEAT_COUNT)
    def test_stop(self):
        """ Test of stopping a task
        """
        # Start the mock task running for 1000 seconds.
        name = 'test_stop'
        cmd = ['python3', 'sip/common/tests/mock_task.py', '1000', '0']
        descriptor = Paas().run_task(name, 'sip', [], cmd)

        # Make sure it is running.
        self._poll_for(TaskStatus.RUNNING, descriptor, timeout=40)
        self.assertEqual(descriptor.status(), TaskStatus.RUNNING)

        # Stop the task
        descriptor.delete()

        self._poll_for(TaskStatus.UNKNOWN, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.UNKNOWN)

    @repeat(REPEAT_COUNT)
    def test_end_in_error(self):
        """ Test of task that exits with an error status
        """
        name = 'test_stop_with_error'
        cmd = ['python3', 'sip/common/tests/mock_task.py', '3', '1']
        descriptor = Paas().run_task(name, 'sip', [], cmd)
        self._poll_for(TaskStatus.ERROR, descriptor)
        self.assertEqual(descriptor.status(), TaskStatus.ERROR)
        descriptor.delete()
        self._poll_for(TaskStatus.UNKNOWN, descriptor)

    @repeat(REPEAT_COUNT)
    def test_duplicate_service(self):
        """ Test trying to start a service twice with the same name
        """
        name = 'test_duplicate_service'
        cmd = ['python3', 'sip/common/tests/mock_service.py', '9999']

        # Start two service tasks with the same name
        tsk1 = Paas().run_service(name, 'sip', [9999], cmd)
        tsk2 = Paas().run_service(name, 'sip', [9999], cmd)

        # Check that the task descriptors are identical.
        self.assertEqual(tsk1.ident, tsk2.ident)

        tsk1.delete()
        self._poll_for(TaskStatus.UNKNOWN, tsk1)
        # FIXME(BM) checking status of the original descriptor gives an error
        # self._poll_for(TaskStatus.UNKNOWN, tsk2)

    @repeat(REPEAT_COUNT)
    def test_duplicate_task(self):
        """ Test trying to start a task twice with the same name
        """
        name = 'test_task_2'
        cmd = ['python3', 'sip/common/tests/mock_service.py', '9999']

        # Start two tasks with the same name
        tsk1 = Paas().run_task(name, 'sip', [], cmd)
        tsk2 = Paas().run_task(name, 'sip', [], cmd)

        # Check that they have identical task descriptors
        self.assertNotEqual(tsk1.ident, tsk2.ident)

        tsk2.delete()
        self._poll_for(TaskStatus.UNKNOWN, tsk2)

    @repeat(REPEAT_COUNT)
    def test_find(self):
        """ Test finding a task
        """
        cmd = ['python3', 'sip/common/tests/mock_task.py', '0', '0']

        # Start the task
        tsk1 = Paas().run_task('test_find', 'sip', [], cmd)

        # Find it
        tsk2 = Paas().find_task('test_find')

        # The descriptor returned from run_task() and find() should be the same
        self.assertEqual(tsk1.ident, tsk2.ident)

        tsk2.delete()
        self._poll_for(TaskStatus.UNKNOWN, tsk2)

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
