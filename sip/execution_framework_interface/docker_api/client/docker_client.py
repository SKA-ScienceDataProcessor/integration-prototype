# -*- coding: utf-8 -*-
"""Docker Client API"""

import docker
import logging
import yaml
import time
import re

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

        with open(docker_stack_file, 'r') as file:
            try:
                s_config = yaml.load(file)
                # self.start_service(s_config)

                # TODO:(NJT) Need to figure out to empty list and
                # dictionary after every loop
                service_spec = {}
                endpoints = {}
                mode = {}
                networks = []

                # TODO: (NJT) Simply Looping the Dictionary
                for config in s_config['services']:
                    service_exist = self._client.services.list(
                        filters={'name': config})
                    if not service_exist:
                        service_spec['name'] = config
                        for key, value in s_config['services'][config].items():
                            time.sleep(2)
                            if 'ports' in key:
                                for port_element in value:
                                    target_port = port_element.split(':')
                                    for port in target_port:
                                        endpoints[int(port)] = int(port)
                                        # #TODO:(NJT) Need to rename new variable
                                        #  to something useful
                                        # new = endpoints.copy()
                                        # new[int(port)] = int(port)
                                endpoint_spec = docker.types.EndpointSpec(
                                    ports=endpoints)
                                service_spec['endpoint_spec'] = endpoint_spec

                            else:
                                if 'volumes' in key:
                                    for volume_element in value:
                                        service_spec[
                                            'mounts'] = volume_element.split()
                                else:
                                    if 'deploy' in key:
                                        for deploy_value in value:
                                            if 'resources' in deploy_value:
                                                resource_spec = DockerClient. \
                                                    parse_resources(value,
                                                                    deploy_value)
                                                service_spec[
                                                    'resources'] = resource_spec
                                            else:
                                                mode[deploy_value] = value[
                                                    deploy_value]
                                                mode_spec = docker.types. \
                                                    ServiceMode(**mode)
                                                service_spec['mode'] = mode_spec

                                    else:
                                        if 'networks' in key:
                                            for n_key, n_value in \
                                                    s_config['networks'].items():
                                                for k, v in n_value.items():
                                                    if 'name' in k:
                                                        networks.append(v)
                                            service_spec['networks'] = networks
                                        else:
                                            service_spec[key] = value

                        print("Service spec")
                        print(service_spec)

                        # Creating Service
                        self._client.services.create(**service_spec)

                        # Clearing all the dict and list
                        networks[:] = []
                        service_spec.clear()
                        endpoints.clear()
                        mode.clear()
                    else:
                        print("Services already exists")

            except yaml.YAMLError as exc:
                print(exc)

    # DONT DELETE NOW, USEFUL CODE
    # def print_keyword_args(self, **kwargs):
    #     list = []
    #     # kwargs is a dict of the keyword args passed to the function
    #     for key, value in kwargs.items():
    #         print("%s = %s" % (key, value))
    #         list.append("%s = %s" % (key, value))

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

    # def start_service(self, config_file):
    #     """
    #     :param config_file:
    #     :return:
    #     """
    #

    ###########################################################################
    # Methods
    ###########################################################################

    @staticmethod
    def parse_resources(value, deploy_value):
        """ Parse resources key
        Rename the key
        Return resources_spec"""

        resources = {}

        for r in value[deploy_value]:
            if 'limits' in r:
                #TODO:(NJT) Need to check if there is a better way to do this
                for r_key, r_value in value[deploy_value][r].items():
                    if 'cpu' in r_key:
                        cpu_value = float(r_value) * 10**9
                        cpu_key = r_key[:3] + '_limit'
                        resources[cpu_key] = int(cpu_value)
                    if 'mem' in r_key:
                        mem_value = re.sub('M', '', r_value)
                        mem_key = r_key[:3] + '_limit'
                        resources[mem_key] = int(mem_value)*1048576
        resource_spec = docker.types.Resources(**resources)
        return resource_spec
