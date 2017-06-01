# -*- coding: utf-8 -*-
""" marathon platform as a service

.. moduleauthor:: Vlad Stolyarov <vlad@mrao.cam.ac.uk>
"""

import json
import os
import time

from sip.common.paas import Paas, TaskDescriptor, TaskStatus

from marathon import MarathonClient
from marathon import models


class MarathonPaas(Paas):

    def __init__(self, marathon_url='http://localhost:8080'):
        """ Constructor

        Args:
            marathon_url (string): URL of the Marathon server

        """

        # Create a marathon client
        self._client = MarathonClient(servers=marathon_url)

    def run_service(self, name, task, ports, cmd_args, restart=True, mem=512, cpus=1.0, instances=1, disk=10):
        """ Run a task as a service.
        """
#        print("Inside run_service 0: ", name, cmd_args)
         # Create new task descriptor
        descriptor = self._new_task_descriptor(name)
 
        # If the service isn't already running start the task as a service
        if descriptor._terminated:
            app = models.app.MarathonApp(id=name, args=cmd_args, mem=mem, cpus=cpus, instances=instances, disk=disk, ports=ports)
            self._client.create_app(app.id, app)
#           Wait until the task is appeared in the task list
            while len(self._client.list_tasks(app_id=name)) == 0 :
                 pass

#           Get the list of tasks
            self._tasks = self._client.list_tasks(app_id=name) 
#            print("Inside run_service 1: ", self._tasks)
            descriptor.ident = self._tasks[0].id
            self._tasks[0].service_ports = ports
#            print("Inside run_service 2: ", descriptor.ident, ports, self._tasks[0].service_ports, app.ports)
            # Bind the docker socket so that the container can talk to the
            # docker engine.
#            mount = docker.types.Mount('/var/run/docker.sock', 
#                    '/var/run/docker.sock', type='bind')

            # Define the restart policy
#            if restart:
#                condition = 'any'
#            else:
#                condition = 'none'
#            restart_policy = docker.types.RestartPolicy(condition=condition)

            # Define the container
#            container_spec = docker.types.ContainerSpec(image=task, 
#                    command=cmd_args[0], args=cmd_args[1:], mounts=[mount])
#            task_template = docker.types.TaskTemplate(
#                    container_spec=container_spec,
#                    restart_policy=restart_policy)

            # Create an endpoints for the ports the services run on.
            #
            # There is (I think) a bug in docker=py which means that
            # we can't get docker to do the port allocation for us.
#            endpoints = {}
#            for target_port in ports:

                # Bind to a free port
#                s = socket.socket()
#                s.bind(('', 0))

                # Get the allocated port name
#                published_port = s.getsockname()[1]

                # Release the port (there is now a race if any other
                # processes are binding to ports but it will do for now)
#                s.close()

                # Add the port to the endpoint spec
                
#                endpoints[published_port] = target_port
#            endpoint_spec = docker.types.EndpointSpec(ports=endpoints)

            # Create the service
#            service = self._client.create_service(task_template, name=name, 
#                    endpoint_spec=endpoint_spec, networks=['sip'])

            # Inspect the service
#            info = self._client.inspect_service(service['ID'])
#            while info['Spec'] == {}:
#                time.sleep(1)
#                info = self._client.inspect_service(service['ID'])

            # Set the host name and port in the task descriptor
            descriptor.hostname = self._get_hostname(name)
            descriptor._target_ports = self._tasks[0].service_ports #{}
            descriptor._published_ports = self._tasks[0].ports #{}
#            if 'Ports' in info['Spec']['EndpointSpec']:
#                endpoint = info['Spec']['EndpointSpec']['Ports']
#                for p in endpoint:
#                    descriptor._target_ports[p['TargetPort']] = \
#                            p['TargetPort']
#                    descriptor._published_ports[p['TargetPort']] = \
#                            p['PublishedPort']

            # Set the ident
#            descriptor.ident = service['ID']

            # Mark the service as not terminated
            descriptor._terminated = False
#            print("Inside run_service 3: ", descriptor.ident,  descriptor.hostname, descriptor._target_ports, descriptor._published_ports )

        return descriptor

    def run_task(self, name, task, ports, cmd_args):
        """ Run a task
        """

        # Create new task descriptor
        descriptor = self._new_task_descriptor(name)

        # Get rid of any existing service with the same name
#        try:
#            self._client.remove_service(name)
#        except:
#            pass

        # Start the task 
#        descriptor = self.run_service(name, task, ports, cmd_args, 
#                restart=False)

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
        descriptor = MarathonTaskDescriptor(name, self._client)


        try:
        # Search for an existing service
#        for task in self._client.list_tasks():
#            if task.id == name:
            
            descriptor.ident = (self._client.list_tasks(app_id=name))[0].id
            descriptor.hostname = self._get_hostname(name)
            descriptor._target_ports = (self._client.list_apps(app_id=name))[0].ports
            descriptor._published_ports = (self._client.list_tasks(app_id=name))[0].ports
            descriptor._terminated = False
#            print("Inside _new_task_decriptor:", descriptor.ident, descriptor.hostname, descriptor._target_ports, descriptor._published_ports, )

#                # Set the ident and host and port number (if there is one)
#                descriptor.ident = task.id
#                if 'Ports' in task['Endpoint']:
#                    descriptor.hostname = self._get_hostname(name)
#                    descriptor._target_ports = {}
#                    descriptor._published_ports = {}
#                    endpoint = task['Endpoint']['Ports']
#                    for p in endpoint:
#                        descriptor._target_ports[p['TargetPort']] = \
#                                p['TargetPort']
#                        descriptor._published_ports[p['TargetPort']] = \
#                                p['PublishedPort']
#
#                # Mark the service as not terminated
#                descriptor._terminated = False
#
#                # Return the descriptor
#            print('Returning exiting descriptor')
            return descriptor
        except:
        # return the empty descriptor
#            print('Returning empty descriptor')
            return descriptor

    def _get_hostname(self, name):
        """ Returns the host name of the machine we are running on.

        The intent is to return a name that can be used to contact
        the task or service.
        """
        return (self._client.list_tasks(app_id=name))[0].host

class MarathonTaskDescriptor(TaskDescriptor):
    def __init__(self, name, client):
        super(MarathonTaskDescriptor, self).__init__(name)
        self._client = client
        self._proc = 0
        self._terminated = True

    def delete(self):
        """ Kill the task
        """

        # Terminate the task
        self._client.delete_app(self.name)

        # Set the state to deleted
        self._terminated = True
        return

    def location(self):
        """ Returns the host and ports of the service of task
        
        The answer depends on whether we are running inside or outside of
        the Docker swarm
        """
#        print("In MarathonPaas::location: ", self.hostname, self._target_ports)

        return self.hostname, self._target_ports

    def status(self):
        """ Return the task status
        """
        try:
            state = (self._client.list_tasks(app_id=self.name))[0].state
        except:
            return TaskStatus.UNKNOWN
        if state == 'TASK_STAGING':
            return TaskStatus.STARTING
        if state == 'TASK_STARTING':
            return TaskStatus.STARTING
        if state == 'TASK_RUNNING':
            return TaskStatus.RUNNING
        if state == 'TASK_FINISHED':
            return TaskStatus.EXITED
        if state == 'TASK_KILLED':
            return TaskStatus.EXITED
        if state == 'TASK_FAILED':
            return TaskStatus.ERROR
        if state == 'TASK_LOST':
            return TaskStatus.ERROR

        return TaskStatus.UNKNOWN

