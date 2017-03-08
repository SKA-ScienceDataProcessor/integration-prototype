# -*- coding: utf-8 -*-
""" popen platform as a service

The popen paas is a paas service that starts tasks using 
the Python subprocess management module. By definition, it is only
capable of managing tasks on the local host.

Its main use is to start various critical services required by the
master controller when the controller is started such as a log
aggregator. It can also be used to "bootstrap" other schedular services
such as ssh or Docker.

.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""

import socket
import subprocess

import abc
from sip_common.paas import Paas, TaskDescriptor, TaskStatus

class PopenPaas(Paas):

    def __init__(self):
        """ Constructor
        """
        self._tasks = {}

    def run_task(self, name, task, cmd_args):
        """ Run a task as a subprocess.
        """

        # Create new task descriptor
        descriptor = self._new_task(name)

        # Start the task
        descriptor._proc = subprocess.Popen(cmd_args, executable=task, 
                shell=False)

        # Set the host name in the task descriptor
        descriptor.host = self._get_hostname()

        # Set the identifier (the process id)
        descriptor.ident = descriptor._proc.pid

        # Return the task descriptor
        return descriptor

    def run_service(self, name, task, port, cmd_args):
        """ Run a service task as a subprocess.
        """

        # Create new task descriptor
        descriptor = self._new_task(name)

        # Start the task
        descriptor._proc = subprocess.Popen(cmd_args, executable=task, 
                shell=False)

        # Set the host name and port in the task descriptor
        descriptor.hostname = self._get_hostname()
        descriptor.port = port

        # Set the identifier (the process id)
        descriptor.ident = descriptor._proc.pid

        # Return the task descriptor
        return descriptor

    def find_task(self, name):
        """ Find task or service
        """
        if name in self._tasks:
            return self._tasks[name]
        return None

    def _new_task(self, name):
        """ Create new task

        Checks that a task with this name doesn't already exist and creates
        a new TaskDescriptor object for it.
        """
        if name in self._tasks:
            return self._tasks[name]
        self._tasks[name] = PopenTaskDescriptor(name, self)
        return self._tasks[name]

    def _get_hostname(self):
        """ Returns the host name of the machine we are running on.

        The intent is to return a name that can be used to contact
        the task or service. This is tricky when the network configuration
        is not straight-forward.
        """
        return socket.gethostname()

class PopenTaskDescriptor(TaskDescriptor):
    def __init__(self, name, paas):
        super(PopenTaskDescriptor, self).__init__(name)
        self._paas = paas
        self._proc = 0
        self._terminated = False

    def delete(self):
        """ Kill the task
        """
        # Terminate the task
        self._proc.terminate()
        self._proc.wait()

        # Set the state to deleted
        self._terminated = True

        # Remove the entry from the dictionary of tasks
        del self._paas._tasks[self.name]
        return

    def status(self):
        """ Return the tasks status
        """
        if self._terminated:
            return TaskStatus.EXITED
            
        # Poll the status
        ret_code = self._proc.poll()
        if ret_code == None:
            result = TaskStatus.RUNNING
        else:
            if ret_code == 0:
                result = TaskStatus.EXITED
            else:
                result = TaskStatus.ERROR
        return result
