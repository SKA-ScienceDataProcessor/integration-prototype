# -*- coding: utf-8 -*-
""" Test of popen platform as a service

Run with:
    $ python3 -m unittest -f -v sip.common.tests.test_popen
or
    $ python3 -m unittest discover -f -v -p test_popen.py


.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""
import os
import sys
import time
import unittest

import rpyc

# pylint: disable=wrong-import-position
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sip.common.popen_paas import PopenPaas as Paas
from sip.common.paas import TaskStatus


class TestPopen(unittest.TestCase):
    """ Tests of a SIP PaaS interface to popen.
    """

    def test_run_task(self):
        """ Test normal execution of task
        """
        # Start the task
        descriptor = Paas().run_task('test_task', 'python3', [],
                                     ['python3',
                                      'sip/common/tests/mock_task.py',
                                      '3', '0'])

        # It should be running
        self.assertEqual(descriptor.status(), TaskStatus.RUNNING)

        # Wait for it to end and it should be ended
        time.sleep(5)
        self.assertEqual(descriptor.status(), TaskStatus.EXITED)

        # Stop the task
        descriptor.delete()

    def test_run_service(self):
        """ Test normal execution of service
        """
        # Start the task
        descriptor = Paas().run_service('test_service', 'python3', 9999,
                                        ['python3',
                                         'sip/common/tests/mock_service.py',
                                         '9999'])

        # It should be running
        self.assertEqual(descriptor.status(), TaskStatus.RUNNING)

        # Wait for it to start
        time.sleep(1)

        # Check that we can talk to it
        (hostname, port) = descriptor.location(9999)
        conn = rpyc.connect(host=hostname, port=port)
        conn.root.hello()

        # Stop the task
        descriptor.delete()

    def test_stop_task(self):
        """ Test of stopping a task
        """
        descriptor = Paas().run_task('test_stop_task', 'python3', [],
                                     ['python3',
                                      'sip/common/tests/mock_task.py',
                                      '3', '0'])

        self.assertEqual(descriptor.status(), TaskStatus.RUNNING)
        descriptor.delete()
        self.assertEqual(descriptor.status(), TaskStatus.EXITED)

    def test_end_in_error(self):
        """ Test of task that exits with an error status
        """
        descriptor = Paas().run_task('test_end_in_error', 'python3', [],
                                     ['python3',
                                      'sip/common/tests/mock_task.py',
                                      '0', '1'])
        time.sleep(1)
        self.assertEqual(descriptor.status(), TaskStatus.ERROR)
        descriptor.delete()

    def test_duplicate(self):
        """ Test trying to start a task twice with the same name
        """
        paas = Paas()

        # Start the task
        tsk1 = paas.run_task('test_duplicate', 'python3', [],
                             ['python3',
                              'sip/common/tests/mock_task.py',
                              '0', '0'])

        # Try another
        tsk2 = paas.run_task('test_duplicate', 'python3', [],
                             ['python3',
                              'sip/common/tests/mock_task.py',
                              '0', '0'])

        self.assertEqual(tsk1.ident, tsk2.ident)

        tsk2.delete()
