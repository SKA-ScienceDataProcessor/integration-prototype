# -*- coding: utf-8 -*-
""" Test of docker platform as a service

.. moduleauthor:; David Terrett <david.terrett@stfc.ac.uk>
"""

import rpyc
import time
import unittest
import warnings

from sip.common.docker_paas import DockerPaas as Paas
from sip.common.paas import TaskStatus

paas = Paas()

class TestDocker(unittest.TestCase):

    # dockerpy keeps the socket to the docker engine open so we need to
    # suppress the resource warning from unittest
    def setUp(self):
        warnings.simplefilter('ignore', ResourceWarning)

    def testTask(self):
        """ Test normal execution of task
        """
        # Start the task
        t = paas.run_task('test_task', 'sip', [],
                ['python3', 'sip/common/test/test_task.py', '5', '0'])
    
        # It should be running
        self._poll_for(TaskStatus.RUNNING, t)
        self.assertEqual(t.status(), TaskStatus.RUNNING)

        # Wait for it to end and it should be ended
        self._poll_for(TaskStatus.EXITED, t)
        self.assertEqual(t.status(), TaskStatus.EXITED)

        # Stop the task 
        t.delete()

    def testService(self):
        """ Test normal execution of service
        """
        # Start the task
        t = paas.run_service('test_service', 'sip', [9999],
                ['python3', 'sip/common/test/test_service.py', '9999'])
    
        # It should be running
        self._poll_for(TaskStatus.RUNNING, t)
        self.assertEqual(t.status(), TaskStatus.RUNNING)

        # Check that we can talk to it
        (hostname, port) = t.location(9999)
        conn = rpyc.connect(host=hostname, port=port)
        conn.root.hello()

        # Stop the task 
        t.delete()
        self._poll_for(TaskStatus.UNKNOWN, t)
        self.assertEqual(t.status(), TaskStatus.UNKNOWN)

    def TestStop(self):
        """ Test of stopping a task
        """
        t = paas.run_task('test_stop', 'sip', [],
                ['python3', 'sip/common/test/test_task.py', '30', '0'])
    
        self._poll_for(TaskStatus.RUNNING, t)
        self.assertEqual(t.status(), TaskStatus.RUNNING)
        t.delete()
        self._poll_for(TaskStatus.UNKNOWN, t)
        self.assertEqual(t.status(), TaskStatus.UNKNOWN)

    #def testEndInError(self):
    #    """ Test of task that exits with an error status
    #    """
    #    t = paas.run_task('test_stop', 'sip', [],
    #            ['python3', 'sip/common/testp/test_task.py', '3', '1'])
    #    time.sleep(10)
    #    self.assertEqual(t.status(), TaskStatus.ERROR)
    #    t.delete()
    #    time.sleep(5)
    
    def testDuplicateService(self):
        """ Test trying to start a service twice with the same name
        """
        # Start the task
        t1 = paas.run_service('test_dup', 'sip', [9999],
                ['python3', 'sip/common/test/test_service.py', '9999'])

        t2 = paas.run_service('test_dup', 'sip', [9999],
                    ['python3', 'sip/common/test/test_service.py', '9999'])

        self.assertEqual(t1.ident, t2.ident)

        t1.delete()
    
    def testDuplicateTask(self):
        """ Test trying to start a task twice with the same name
        """
        # Start the task
        t1 = paas.run_task('test_task', 'sip', [],
                ['python3', 'sip/common/testp/test_service.py', '9999'])
    
        # Try another
        t2 = paas.run_task('test_task', 'sip', [],
                ['python3', 'sip/common/testp/test_service.py', '9999'])

        self.assertNotEqual(t1.ident, t2.ident)
        t2.delete()

    def testFind(self):
        """ Test finding a task
        """
        # Start the task
        t1 = paas.run_task('test_find', 'sip', [],
                ['python3', 'sip/common/test/test_task.py', '0', '0'])

        # Find it
        t2 = paas.find_task('test_find')

        self.assertEqual(t1.ident, t2.ident)
        t2.delete()

    def _poll_for(self, status, descr):
        n = 0
        while not descr.status() == status:
            if n == 10:
                self.fail('task not {} after 10s'.format(status))
            n = n + 1 
            time.sleep(1)
