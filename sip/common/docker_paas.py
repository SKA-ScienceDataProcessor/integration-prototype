# -*- coding: utf-8 -*-
""" docker platform as a service

.. moduleauthor:: David Terrett <david.terrett@stfc.ac.uk>
"""

import docker
import json
import socket
import re
import os
import time

import abc
from sip.common.paas import Paas, TaskDescriptor, TaskStatus

_nextport = 10000

class DockerPaas(Paas):

    def __init__(self, docker_url='unix:///var/run/docker.sock'):
        """ Constructor

        Args:
            docker_url (string): URL of the docker engine

        The docker engine must be a manager of a swarm.
        """

        # Create a docker client
        self._client = docker.APIClient( base_url=docker_url)

    def run_service(self, name, task, ports, cmd_args, restart=True):
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

            # Define the restart policy
            if restart:
                condition = 'any'
            else:
                condition = 'none'
            restart_policy = docker.types.RestartPolicy(condition=condition)

            # Define the container
            container_spec = docker.types.ContainerSpec(image=task, 
                    command=cmd_args[0], args=cmd_args[1:], mounts=[mount])
            task_template = docker.types.TaskTemplate(
                    container_spec=container_spec,
                    restart_policy=restart_policy)

            # Create an endpoints for the ports the services run on.
            #
            endpoints = {}
            global _nextport
            for p in ports:
                endpoints[_nextport] = p
                _nextport = _nextport + 1
            endpoint_spec = docker.types.EndpointSpec(ports=endpoints)

            # Create the service
            service = self._client.create_service(task_template, name=name, 
                    endpoint_spec=endpoint_spec, networks=['sip'])

            # Inspect the service
            info = self._client.inspect_service(service['ID'])
            while info['Spec'] == {}:
                time.sleep(1)
                info = self._client.inspect_service(service['ID'])

            # Set the host name and port in the task descriptor
            descriptor.hostname = self._get_hostname(name)
            descriptor._target_ports = {}
            descriptor._published_ports = {}
            if 'Ports' in info['Spec']['EndpointSpec']:
                endpoint = info['Spec']['EndpointSpec']['Ports']
                for p in endpoint:
                    descriptor._target_ports[p['TargetPort']] = \
                            p['TargetPort']
                    descriptor._published_ports[p['TargetPort']] = \
                            p['PublishedPort']

            # Set the ident
            descriptor.ident = service['ID']

            # Mark the service as not terminated
            descriptor._terminated = False

        return descriptor

    def run_task(self, name, task, ports, cmd_args):
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
        descriptor = self.run_service(name, task, ports, cmd_args, 
                restart=False)

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
                if 'Ports' in task['Endpoint']:
                    descriptor.hostname = self._get_hostname(name)
                    descriptor._target_ports = {}
                    descriptor._published_ports = {}
                    endpoint = task['Endpoint']['Ports']
                    for p in endpoint:
                        descriptor._target_ports[p['TargetPort']] = \
                                p['TargetPort']
                        descriptor._published_ports[p['TargetPort']] = \
                                p['PublishedPort']

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

    def location(self):
        """ Returns the host and ports of the service of task
        
        The answer depends on whether we are running inside or outside of
        the Docker swarm
        """
        if os.path.exists("docker_swarm"):
            return self.hostname, self._target_ports
        else:
            return self.hostname, self._published_ports

    def status(self):
        """ Return the task status
        """
        try:
            state = self._client.inspect_task(self.name)['Status']['State']
        except:
            return TaskStatus.UNKNOWN
        if state == 'new':
            return TaskStatus.STARTING
        if state == 'preparing':
            return TaskStatus.STARTING
        if state == 'running':
            return TaskStatus.RUNNING
        if state == 'complete':
            return TaskStatus.EXITED
        if state == 'failed':
            return TaskStatus.ERROR
