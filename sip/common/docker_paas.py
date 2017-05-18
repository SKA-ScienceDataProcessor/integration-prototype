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

class DockerPaas(Paas):

    def __init__(self):
        """ Constructor
        """

        # Create a docker client
        self._client = docker.from_env();

        # Store a flag to show whether we are on a manager node or a 
        # worker.
        self._manager = self._client.info()['Swarm']['ControlAvailable']

    def run_service(self, name, task, ports, cmd_args, restart=True):
        """ Run a task as a service.

        Only manager nodes can create a service
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be run on swarm manager nodes')

        # Try to get a descriptor for this service
        descriptor = self.find_task(name)
        if not descriptor:

            # If the service isn't already running start the task as a service

            # Define a mount so that the container can talk to the
            # docker engine.
            mount = ['/var/run/docker.sock:/var/run/docker.sock:rw']

            # Define the restart policy
            if restart:
                condition = 'any'
            else:
                condition = 'none'
            restart_policy = docker.types.RestartPolicy(condition=condition)
 
            # Create an endpoints for the ports the services run on.
            #
            # There is (I think) a bug in docker=py which means that
            # we can't get docker to do the port allocation for us.
            endpoints = {}
            for target_port in ports:
 
                # Bind to a free port
                s = socket.socket()
                s.bind(('', 0))
 
                # Get the allocated port name
                published_port = s.getsockname()[1]

                # Release the port (there is now a race if any other
                # processes are binding to ports but it will do for now)
                s.close()

                # Add the port to the endpoint spec
            
                endpoints[published_port] = target_port
            endpoint_spec = docker.types.EndpointSpec(ports=endpoints)

            # Create the service
            service = self._client.services.create(image=task, 
                    command=cmd_args[0], args=cmd_args[1:],
                    endpoint_spec=endpoint_spec, name=name,
                    networks=['sip'], mounts=mount,
                        restart_policy=restart_policy);

            # Create a new descriptor now that the service is running. We
            # need to sleep to give docker time to configure the new service
            # and show up in the list of services.
            time.sleep(2)
            descriptor = DockerTaskDescriptor(name)
        return descriptor

    def run_task(self, name, task, ports, cmd_args):
        """ Run a task

        A task is the same as a service except that it is not restarted
        if it exits.

        Only manager nodes can create a service
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be run on swarm manager nodes')

        # Get rid of any existing service with the same name
        d = self.find_task(name)
        if d:
            d.delete()

        # Start the task 
        descriptor = self.run_service(name, task, ports, cmd_args, 
                restart=False)

        return descriptor

    def find_task(self, name):
        """ Find a task or service

        Returns a TaskDescriptor for the task or None if the task
        doesn't exist. Note that on a worker node there is no check on
        whether the task really exists and the descriptor may not point
        to real task.
        """
        try:
            return DockerTaskDescriptor(name)
        except:
            return None

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
    def __init__(self, name):
        super(DockerTaskDescriptor, self).__init__(name)
        self._proc = 0

        # See if we are a manager node
        paas = DockerPaas();
        self._manager = paas._manager
        if self._manager:

            # Search for an existing service with this name
            self._service = paas._client.services.list(filters={'name':name})
            if len(self._service) > 0:

                # Get the ident
                self.ident = self._service[0].id

                # Get host and port number(if there are any)
                self.hostname = paas._get_hostname(name)
                attrs = self._service[0].attrs
                if 'Ports' in attrs['Endpoint']:
                    self._target_ports = {}
                    self._published_ports = {}
                    ports = attrs['Endpoint']['Ports']
                    for p in ports:
                        self._target_ports[p['TargetPort']] = p['TargetPort']
                        self._published_ports[p['TargetPort']] = \
                                    p['PublishedPort']
            else:
                raise RuntimeError('task "{}" not found'.format(name))

    def delete(self):
        """ Kill the task

        Only manager nodes can delete a service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        # Remove the service
        if len(self._service):
            self._service[0].remove()
        self._service = []

        return

    def location(self, port):
        """ Returns the host and ports of the service or task
        
        The answer depends on whether we are running inside or outside of
        the Docker swarm. If we are a container running inside the swarm
        the ports are the target ports whereas if we are outside the swarm
        we want the published port
        """
        if os.path.exists("docker_swarm"):
            return self.hostname, port
        else:
            return self.hostname, self._published_ports[port]

    def status(self):
        """ Return the task status
        """
        state = 'unknown'
        if len(self._service) > 0:

            # Reload the service attributes from the docker engine
            self._service[0].reload()

            # Look at the status of all the tasks in this service
            # looking for the "best"
            for task in self._service[0].tasks():

                # Don't know who to do this really - for the moment just see
                # if there is one running.
                s = task['Status']['State']
                if s == 'running':
                    state = s
                    break

        # Return the corresponding TaskStatus value.
        if state == 'unknown':
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
