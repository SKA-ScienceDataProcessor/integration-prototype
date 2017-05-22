# -*- coding: utf-8 -*-
""" Platform as a service interface.

The Pass class defines the interface to schedulers. Schedulers are
services that start, stop and monitor tasks on behalf of the master
controller. 

.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""

import abc
from enum import Enum

class Paas(metaclass=abc.ABCMeta):
    """ Platform as a service interface

    The Paas interface distiguished between two sorts of task; ones
    which are expected to run until shut down explictily (called services)
    and those which are expected to exit themselves after completing some
    task (called tasks). 

    The PAAS is expected to restart services if they fail but not tasks.

    Once created, a task or service is controlled with an object called
    a TaskDescriptor which is either created either when the service or
    task is created or the find_task method which searches for an already
    running task or service.

    Services typically listen on one or more IP ports where the port numbers
    are defined as part of the interface. The task descriptor's location
    method translates a service port number into the host name and actual port
    that should be used to access the service.
    """

    @abc.abstractmethod
    def run_task(self, name, task, ports, args):
        """  Run a task.
        
        Args:
            name: Task name. Any string but must be unique.
            task: Task to run (e.g. the name of an executable image).
            ports: A list of TCP ports (int) used by the task.
            args: A list of command line argument for the task.

        Returns:
            TaskDescriptor for the task,
        """

    @abc.abstractmethod
    def run_service(self, name, task, ports, args):
        """  Run a task as a service.
        
        Args:
            name: Service name. Any string but must be unique.
            task: Task to run (e.g. the name of an executable image).
            ports: A list of TCP ports (int) used by the task.
            args: A list of command line argument for the task.

        Returns:
            TaskDescriptor for the task,
        """
        pass

    @abc.abstractmethod
    def find_task(self, name):
        """ Returns a descriptor for the task or service or None"

        Args:
            name (string): task name

        Returns:
            a TaskDescriptor object or None if the task can't be found
        """
        pass

class TaskStatus(Enum):
    """ Task or service states
    """
    RUNNING = 1
    EXITED = 2
    ERROR = 3
    UNKNOWN = 4
    STARTING = 5

class TaskDescriptor:
    """ Task descriptor

    A task descriptor is an object that enables a client to interact
    with a task or service; inquiring its status and properties and 
    deleting it.
    """
    def __init__(self, name):
        """ Constructor
    
        Args:
            name: Task name
        """
        self.name = name

    @abc.abstractmethod
    def delete(self):
        """ Stop and delete the task or service.

        When a task is deleted it is removed from the list of tasks
        being controlled by the service.
        """
        pass

    @abc.abstractmethod
    def status(self):
        """ Get status of the task or service.

        Returns:
            The task status.
        """
        pass

    @abc.abstractmethod
    def location(self, port):
        """ Get the location of a task or service

        Args:
            port: The port the service runs on.

        Returns: 
            The host name and port for connecting to the service.
        """
        pass
