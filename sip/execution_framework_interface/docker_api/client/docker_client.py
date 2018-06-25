# -*- coding: utf-8 -*-
"""Docker Client API"""

import docker
import logging
import yaml
import time

from ast import literal_eval

LOG = logging.getLogger('SIP.EFI.DC')


class DockerClient:
    """Docker Client Interface"""

    def __init__(self):
        """ Constructor of the class"""

        # Create a docker client
        self._client = docker.from_env()

        # Store a flag to show whether we are on a manager node or a
        # worker.
        self._manager = self._client.info()['Swarm']['ControlAvailable']

        # Docker low-level API
        self._api_client = docker.APIClient()

    ###########################################################################
    # Create functions
    ###########################################################################

    def create_service(self, docker_stack_file):
        """

        Args:
        """


        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be run on swarm manager nodes')

        with open(docker_stack_file, 'r') as config:
            try:
                stack_config = yaml.load(config)
                service_list = self.parse_config(stack_config)
                for service_spec in service_list:
                    print(service_spec)
                    # self._client.services.create(**service_spec)
                    # time.sleep(2)
                # for name in stack_config['services']:
                #     service_exist = self._client.services.list(
                #         filters={'name': name})
                #     if not service_exist:
                #         service_list = self.parse_config(stack_config)
                #
                #         for service_spec in service_list:
                #             print(service_spec)
                           # self._client.services.create(**service_spec)
                           # time.sleep(2)




                    #print_keyword_args(first_name="John", last_name="Doe")

                    # for key, value in service_spec.items():
                    #     list.append(value)
                    #
                    # print(list)

                  #  print("%s=%s" %(*service_spec, ' ')

                   #print(list)

                   # self._client.services.create(*service_spec, endpoint_spec)

                    #volumes = stack_config['services'][name]['volumes']

                    # self._client.services.create(
                    #     name='config_database',
                    #     image='redis:4.0.6-alpine', endpoint_spec = endpoint_spec, mounts = ['config_database1:/data/db'])

                    # task = stack_config['services'][name]['image']
                    # ports = stack_config['services'][name]['ports']
                    # volumes = stack_config['services'][name]['volumes']
                    #
                    #
                    # for element in ports:
                    #     target_port = element.split(':')
                    #     for port in target_port:
                    #         endpoints[int(port)] = int(port)
                    #
                    # # Add the port to the endpoint spec
                    # endpoint_spec = docker.types.EndpointSpec(
                    #     ports=endpoints)
                    #
                    #
                    #
                    # print(task)
                    # print(endpoint_spec)
                    #print(volumes)

                        #
                        # self._client.services.create(
                        #     image=task, endpoint_spec=endpoint_spec,
                        #     name=name, mounts=volumes)

            except yaml.YAMLError as exc:
                print(exc)

    # def print_keyword_args(self, **kwargs):
    #     list = []
    #     # kwargs is a dict of the keyword args passed to the function
    #     for key, value in kwargs.items():
    #         print("%s = %s" % (key, value))
    #         list.append("%s = %s" % (key, value))


        # # Check if there is a service running in this name
        # service_exist = self._client.services.list(filters={'name': name})
        # if not service_exist:
        #     #TODO(NJT): NEED TO MODIFY THIS
        #     service = self._client.services.create(image='busybox', command=[
        #         'echo', 'hello'], name="testing_service")

            # If the service isn't already running start the task as a service

    def create_volume(self):
        """

        Args:
        """
        pass

    ###########################################################################
    # Delete functions
    ###########################################################################

    def delete_service(self, name):
        """ Removes/stops a service

        Only the manager nodes can delete a service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        # Remove the service
        self._api_client.remove_service(name)

    def delete_all_services(self):
        """ Removes/stops a service

        Only the manager nodes can delete a service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        _service_list = self.get_service_list()
        for _services in _service_list:
            # Remove all the services
            self._api_client.remove_service(_services.id)

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_node_list(self):
        """ Get a list of nodes

        Only the manager nodes can retrieve all the services
        Args:
        """
        # Initialise variables
        nodes = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        _list = self._client.nodes.list()
        for _node_list in _list:
            nodes.append(_node_list.id)
        return nodes

    def get_node_details(self, node_id):
        """ Get details of a node

        Args:
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        _node = self._client.nodes.get(node_id)
        return _node.attrs

    def get_service_list(self):
        """ Get a list of service

        Only the manager nodes can retrieve all the services
        Args:
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        _service_list = self._client.services.list()
        return _service_list

    def get_service_details(self, service_id):
        """ Get details of a service

        Args:
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError(\
                'Services can only be deleted on swarm manager nodes')

        _service = self._client.services.get(service_id)
        return _service.attrs

    def get_volume(self):
        """ Get a volume

        Args:
        """
        pass

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_service(self):
        """ Update a service's configuration.

        Args:
        """
        pass

    def update_node(self, name, labels):
        """Update node's configuration

          Args:
            name (string): Name of the node.
            labels (dict): Label to add to the node
        """

        #TODO:(NJT) Need to think about wether to create the spec inside this
        #TODO: function. Probably best to do it inside the function
        pass

    def parse_config(self, config_file):
        """
        :param config_file:
        :return:
        """
        service_spec = {}
        endpoints = {}
        list = []

        #TODO: (NJT) Simply Looping the Dictionary
        output = yaml.dump(config_file)
        print(output)
        for config in config_file['services']:
            service_spec['name'] = config
            for key, value in config_file['services'][config].items():
                time.sleep(2)
                if 'ports' in key:
                    for port_element in value:
                        target_port = port_element.split(':')
                        for port in target_port:
                            #TODO:(NJT) Need to rename new variable to something useful
                            new = endpoints.copy()
                            new[int(port)] = int(port)
                else:
                    if 'volumes' in key:
                        for volume_element in value:
                            # print(elements)
                            service_spec['mounts'] = volume_element.split()

                    else:
                        service_spec[key] = value

            # Add the port to the endpoint spec
            endpoint_spec = docker.types.EndpointSpec(
                ports=new)
            service_spec['endpoint_spec'] = endpoint_spec

            print(service_spec)

            # TODO:(NJT) Need to figure out to layout the function, service create function needs to be here

            self._client.services.create(**service_spec)

        return list
