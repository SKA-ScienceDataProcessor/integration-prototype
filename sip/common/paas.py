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
    """ Paas interface
    """

    @abc.abstractmethod
    def run_task(self, name, task, ports, args):
        """  Run a task.
        
        Args:
            name (string): Task name. Any string but must be unique.
            task (string): Task to run (e.g. executable image)
            ports (int): TCP ports used by the task
            args (list): Command line to run the task.
        """

    @abc.abstractmethod
    def run_service(self, name, task, ports, args):
        """  Run a task as a service.
        
        Args:
            name (string): Task name. Any string but must be unique.
            task (string): Task to run (e.g. executable image)
            ports (int): TCP ports used by the service
            args (list): Command line to run task task.
        """
        pass

    @abc.abstractmethod
    def find_task(self, name):
        """ Returns a descriptor for the task or service or None"

        Args:
            name (string): task name

        Returns:
            a task descriptor or None
        """
        pass

class TaskStatus(Enum):
    RUNNING = 1
    EXITED = 2
    ERROR = 3
    UNKNOWN = 4
    STARTING = 5

class TaskDescriptor:
    """ Task descriptor

    A task descriptor is an object that enables a client to interact
    with a task; inquiring its status and properties and deleting it.

    Four properties are defined by default:

        task (string): The task name
        hostname (string): The name of the host the task is running on.
        ports (dict): A dictionary that maps from the ports the service
                      exposes to ports on hostname
        ident (string): Some sort of unique identifier

    If the task is not a service the port will be zero.   
    """
    def __init__(self, name):
        """ Constructor
    
        Args:
            name (string): Task name
        """
        self.name = name
        self.hostname = None
        self.ports = {}
        self.ident = None

    @abc.abstractmethod
    def delete(self):
        """ Stop and delete the task.

        When a task is deleted it is removed from the list of tasks
        being controlled by the service.
        """
        pass

    @abc.abstractmethod
    def status(self):
        """ Get status of the tasks.

        Returns:
            The task status.
        """
        pass

    def location(self):
        """ Get the location of a task or service

        The default implementation just returns the hostname and ports
        stored in the descripter object. Other implementations may do
        something more dynamic.
        """
        return self.hostname, self.ports

