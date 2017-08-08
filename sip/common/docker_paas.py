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
        self._client = docker.from_env()

        # Store a flag to show whether we are on a manager node or a 
        # worker.
        self._manager = self._client.info()['Swarm']['ControlAvailable']

    def run_service(self, name, task, ports, cmd_args, restart=True,
            constraints=[]):
        """ Run a task as a service.

        Only manager nodes can create a service

        Args:
            name: Task name. Any string but must be unique.
            task: Task to run (e.g. the name of an executable image).
            ports: A list of TCP ports (int) used by the task.
            args: A list of command line argument for the task.

        Returns:
            DockerTaskDescriptor for the task,
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

            	# Add the port to the dictionary of ports
                endpoints[published_port] = target_port

            # Add the port to the endpoint spec
            endpoint_spec = docker.types.EndpointSpec(ports=endpoints)

            # Create the service
            service = self._client.services.create(image=task, 
                    command=cmd_args[0], 
                    args=cmd_args[1:],
                    endpoint_spec=endpoint_spec, 
                    name=name,
                    networks=['sip'], 
                    mounts=mount,
                    restart_policy=restart_policy,
                    constraints=constraints);

            # Create a new descriptor now that the service is running. We
            # need to sleep to give docker time to configure the new service
            # and show up in the list of services.
            time.sleep(2)
            descriptor = DockerTaskDescriptor(name)
        return descriptor

    def run_task(self, name, task, ports, cmd_args, host=None):
        """ Run a task

        A task is the same as a service except that it is not restarted
        if it exits.

        Only manager nodes can create a service

        Args:
            name: Task name. Any string but must be unique.
            task: Task to run (e.g. the name of an executable image).
            ports: A list of TCP ports (int) used by the task.
            args: A list of command line argument for the task.

        Returns:
            DockerTaskDescriptor for the task,
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be run on swarm manager nodes')

        # Get rid of any existing service with the same name
        d = self.find_task(name)
        if d:
            d.delete()

        # Define the constraints
        constraints = []
        if node != None:
            constraints.append('node.hostname == {}'.format(host))

        # Start the task 
        descriptor = self.run_service(name, task, ports, cmd_args, 
                restart=False, constraints=constraints)

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
        """
        Args:
            name: Task name
        """
        super(DockerTaskDescriptor, self).__init__(name)
        self.ident = 0

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
                self._hostname = paas._get_hostname(name)
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
        else:

            # If we are not a manager the best we can do is assume that the
            # service is running and the network is mapping the service
            # name to the correct host.
            self._hostname = name

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
        """ Get the location of a task or service

        Args:
            port: The advertised port for the.

        Returns: 
            The host name and port for connecting to the service.
        
        The answer depends on whether we are running inside or outside of
        the Docker swarm. If we are a container running inside the swarm
        the ports are the target ports and the host name is the same as
        the name of the service and the port is the same. If we are outside 
        the swarm the host is the manager node that we are running on and
        the port is the published port the port was mapped to.
        """
        if os.path.exists("docker_swarm"):
            return self.name, port
        else:
            return self._hostname, self._published_ports[port]

    def status(self):
        """ Return the task status

        Returns:
            The task status as a TaskStatus enum.
        """
        state = 'unknown'
        if len(self._service) > 0:

            # Reload the service attributes from the docker engine
            self._service[0].reload()

            # Look at the status of all the tasks in this service
            # looking for the "best". 
            #
            # The possible states are:
            #    pending
            #    created
            #    running
            #    ready
            #    starting
            #    preparing
            #    removing
            #    paused
            #    complete
            #    failed
            #    dead
            #
            # First look for a container in the running or paused state
            for task in self._service[0].tasks():
                if (task['Status']['State'] == 'running') or (
                    task['Status']['State'] == 'paused'):
                     return TaskStatus.RUNNING

            # If that failed, look for one that is starting
            for task in self._service[0].tasks():
                if (task['Status']['State'] == 'created' ) or (
                    task['Status']['State'] == 'starting') or (
                    task['Status']['State'] == 'preparing') or (
                    task['Status']['State'] == 'pending') or (
                    task['Status']['State'] == 'ready'):
                     return TaskStatus.STARTING

            # Look for exiting or exited or dead
            for task in self._service[0].tasks():
                if (task['Status']['State'] == 'removing' ) or (
                    task['Status']['State'] == 'complete') or (
                    task['Status']['State'] == 'dead'):
                     return TaskStatus.EXITED

            # Look for error
            for task in self._service[0].tasks():
                if (task['Status']['State'] == 'failed'):
                     return TaskStatus.ERROR

            # Check for some other state and log it
            for task in self._service[0].tasks():
                print('Unexpected Docker container state "{}"'.format(
                        task['Status']['State']))
            return TaskStatus.UNKNOWN
        return TaskStatus.UNKNOWN
