# -*- coding: utf-8 -*-
""" Test of popen platform as a service

Run with:
    $ python3 -m unittest -f -v sip.common.test.test_popen
or
    $ python3 -m unittest discover -f -v -p test_popen.py


.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""
import os
import sys
import time
import unittest

import rpyc

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sip.common.popen_paas import PopenPaas as Paas
from sip.common.paas import TaskStatus


class TestPopen(unittest.TestCase):
    def testTask(self):
        """ Test normal execution of task
        """
        s = Paas()

        # Start the task
        t = s.run_task('test', 'python3', [],
                       ['python3', 'sip/common/test/mock_task.py', '3', '0'])

        # It should be running
        self.assertEqual(t.status(), TaskStatus.RUNNING)

        # Wait for it to end and it should be ended
        time.sleep(5)
        self.assertEqual(t.status(), TaskStatus.EXITED)

        # Stop the task
        t.delete()

    def testService(self):
        """ Test normal execution of service
        """
        s = Paas()

        # Start the task
        t = s.run_service('test', 'python3', 9999,
                          ['python3', 'sip/common/test/mock_service.py',
                           '9999'])

        # It should be running
        self.assertEqual(t.status(), TaskStatus.RUNNING)

        # Wait for it to start
        time.sleep(1)

        # Check that we can talk to it
        (hostname, port) = t.location(9999)
        conn = rpyc.connect(host=hostname, port=port)
        conn.root.hello()

        # Stop the task
        t.delete()

    def testStop(self):
        """ Test of stopping a task
        """
        s = Paas()
        t = s.run_task('test', 'python3', [],
                       ['python3', 'sip/common/test/mock_task.py', '3', '0'])

        self.assertEqual(t.status(), TaskStatus.RUNNING)
        t.delete()
        self.assertEqual(t.status(), TaskStatus.EXITED)

    def testEndInError(self):
        """ Test of task that exits with an error status
        """
        s = Paas()
        t = s.run_task('test', 'python3', [],
                       ['python3', 'sip/common/test/mock_task.py', '0', '1'])
        time.sleep(1)
        self.assertEqual(t.status(), TaskStatus.ERROR)
        t.delete()

    def testDuplicate(self):
        """ Test trying to start a task twice with the same name
        """
        s = Paas()

        # Start the task
        t1 = s.run_task('test', 'python3', [],
                        ['python3', 'sip/common/test/mock_task.py', '0', '0'])

        # Try another
        t2 = s.run_task('test', 'python3', [],
                        ['python3', 'sip/common/test/mock_task.py', '0', '0'])

        self.assertEqual(t1.ident, t2.ident)

        t2.delete()
