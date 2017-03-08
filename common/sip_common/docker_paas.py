# -*- coding: utf-8 -*-
""" docker platform as a service

.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""

import docker
import json
import socket
import re
import os

import abc
from sip_common.paas import Paas, TaskDescriptor, TaskStatus

class DockerPaas(Paas):

    def __init__(self, docker_url='unix:///var/run/docker.sock'):
        """ Constructor

        Args:
            docker_url (string): URL of the docker engine

        The docker engine must be a manager of a swarm.
        """

        # Create a docker client
        self._client = docker.APIClient( base_url=docker_url)

    def run_service(self, name, task, port, cmd_args):
        """ Run a task as a service.
        """

        # Create new task descriptor
        descriptor = self._new_task_descriptor(name)

        # If the service isn't already running start the task as a service
        if descriptor._terminated:

            # Bind the docker socket so that the container can talk to the
            # docker engine.
            mount = docker.types.Mount('/var/run/docker.sock', 
                    '/var/run/docker.sock', type='bind')

            # Define the container
            container_spec = docker.types.ContainerSpec(image=task, 
                    command=cmd_args[0], args=cmd_args[1:], mounts=[mount])
            task_template = docker.types.TaskTemplate(
                    container_spec=container_spec)

            # Create an endpoint for the port the service will run on.
            #
            # (the second port at port+100 is a temporary kludge for
            # the heartbeat which we will be getting rid of)
            endpoint_spec = docker.types.EndpointSpec(ports={
                port: port, port+100: port+100})

            # Create the service
            service = self._client.create_service(task_template, name=name, 
                    endpoint_spec=endpoint_spec, networks=['sip'])

            # Set the host name and port in the task descriptor
            descriptor.hostname = self._get_hostname(name)
            descriptor.port = port

            # Set the ident
            descriptor.ident = service['ID']

            # Mark the service as not terminated
            descriptor._terminated = False

        return descriptor

    def run_task(self, name, task, cmd_args):
        """ Run a task
        """

        # Create new task descriptor
        descriptor = self._new_task_descriptor(name)

        # Get rid of any existing service with the same name
        try:
            self._client.remove_service(name)
        except:
            pass

        # Start the task 
        # Kudlge alert - we need to specify some port so that the kudge
        # for the heartbeat port works.
        descriptor = self.run_service(name, task, 1000, cmd_args)

        return descriptor

    def find_task(self, name):
        """ Find a task or service
        """
        descriptor = self._new_task_descriptor(name)
        if descriptor._terminated:
            return None
        return descriptor

    def _new_task_descriptor(self, name):
        """ Create a task descriptor 

        Args 
            name (string): task name
        """

        # Create new descriptor
        descriptor = DockerTaskDescriptor(name, self._client)

        # Search for an existing service
        for task in self._client.services():
            if task['Spec']['Name'] == name:

                # Set the ident and host and port number (if there is one)
                descriptor.ident = task['ID']
                if 'Endpoint' in task:
                    descriptor.hostname = self._get_hostname(name)
                    descriptor.port = \
                            task['Endpoint']['Ports'][0]['PublishedPort']

                # Mark the service as not terminated
                descriptor._terminated = False

                # Return the descriptor
                return descriptor

        # return the empty descriptor
        return descriptor

    def _get_hostname(self, name):
        """ Returns the host name of the machine we are running on.

        The intent is to return a name that can be used to contact
        the task or service.
        """

        # If we are in a docker container then the host name is the same as
        # the service name
        if os.path.exists('/.dockerenv'):
            return socket.gethostbyname(name)

        # If not, assume we are a swarm master and return localhost
        return 'localhost'

class DockerTaskDescriptor(TaskDescriptor):
    def __init__(self, name, client):
        super(DockerTaskDescriptor, self).__init__(name)
        self._client = client
        self._proc = 0
        self._terminated = True

    def delete(self):
        """ Kill the task
        """

        # Terminate the task
        self._client.remove_service(self.name)

        # Set the state to deleted
        self._terminated = True
        return

    def status(self):
        """ Return the task status
        """
        s = self._client.inspect_service(self.name)
        return TaskStatus.RUNNING
