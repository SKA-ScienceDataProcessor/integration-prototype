# -*- coding: utf-8 -*-
"""Docker Client API"""

import docker
import logging
import yaml
import re
import os

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

    def create_services(self, compose_file):
        """ Create new services

        Args:
            compose_file (file): Docker compose file
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be run on swarm manager nodes')

        with open(compose_file, 'r') as file:
            try:
                s_config = yaml.load(file)
                for config in s_config['services']:
                    service_exist = self._client.services.list(
                        filters={'name': config})
                    if not service_exist:
                        service_spec = self.parse_service(s_config, config)
                        for s_spec in service_spec:
                            print("Service Spec: ", s_spec)
                            self._client.services.create(**s_spec)
                    else:
                        print("Services already exists")

            except yaml.YAMLError as exc:
                print(exc)

    def create_volume(self, volume_name, driver_spec=None):
        """ Create new volumes
        Args:
            volume_name (string): Name to create docker volume
            driver_spec (string): Driver for the docker volume
        """

        # Default values
        if driver_spec:
            _driver = driver_spec
        else:
            _driver = 'local'

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        self._client.volumes.create(name=volume_name, driver=_driver)

    ###########################################################################
    # Delete functions
    ###########################################################################

    def delete_service(self, service_name):
        """ Removes/stops a service

        Only the manager nodes can delete a service

        Args:
            service_name (string): Name of the service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        # Remove the service
        self._api_client.remove_service(service_name)

    def delete_all_services(self):
        """ Removes/stops a service

        Only the manager nodes can delete a service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

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
        """
        # Initialise variables
        _nodes = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node '
                               'can retrieve all the nodes.')

        _list = self._client.nodes.list()

        for _node_list in _list:
            _nodes.append(_node_list.id)
        return _nodes

    def get_node_details(self, node_id):
        """ Get details of a node

        Args:
            node_id (list): List of node ID
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can '
                               'retrieve node details.')

        _node = self._client.nodes.get(node_id)
        return _node.attrs

    def get_service_list(self):
        """ Get a list of service

        Only the manager nodes can retrieve all the services
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve'
                               ' all the services.')

        _service_list = self._client.services.list()
        return _service_list

    def get_service_details(self, service_id):
        """ Get details of a service

        Args:
            service_id (list): List of service ID
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve all'
                               ' the services details.')

        _service = self._client.services.get(service_id)
        return _service.attrs

    def get_volume_details(self, volume_name):
        """ Get details of the volume

        Args:
            volume_name (string): Name of the volume
        """

        _volume = self._client.volumes.get(volume_name)
        return _volume.attrs

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_service(self):
        """ Update a service's configuration.

        Args:
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can update '
                               'services details.')

    def update_node(self, name, labels):
        """Update node's configuration

          Args:
            name (string): Name of the node.
            labels (dict): Label to add to the node
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can update '
                               'node details.')

        #TODO:(NJT) Need to think about wether to create the spec inside this
        #TODO: function. Probably best to do it inside the function
        pass

    ###########################################################################
    # Parsing functions
    ###########################################################################

    def parse_service(self, s_config, config):
        """Parsing the docker compose file

        Args:
            s_config ():
            config ():
        """
        # Initialising empty dictionary and list
        _service_spec = {}
        _endpoints = {}
        _mode = {}

        networks = []

        _service_spec['name'] = config
        for key, value in s_config['services'][config].items():
            # time.sleep(2)
            if 'ports' in key:
                for port_element in value:
                    target_port = port_element.split(':')
                    for port in target_port:
                        _endpoints[int(port)] = int(port)
                endpoint_spec = docker.types.EndpointSpec(ports=_endpoints)
                _service_spec['endpoint_spec'] = endpoint_spec
            else:
                if 'volumes' in key:
                    for volume_element in value:
                        for v_key, v_value in volume_element.items():
                            if v_key == 'source':
                                if v_value == '.':
                                    source = os.path.dirname(
                                        os.path.abspath(__file__))
                                else:
                                    source = v_value
                            if v_key == 'target':
                                target = v_value
                        volume = [source + ':' + target]
                        _service_spec['mounts'] = volume

                        #Don't delete this now
                        #service_spec['mounts'] = volume_element.split()
                else:
                    if 'deploy' in key:
                        for d_value in value:
                            if 'restart_policy' in d_value:
                                restart_spec = docker.types.RestartPolicy(
                                    **value[d_value])
                                _service_spec['restart_policy'] = restart_spec

                            if 'mode' in d_value:
                                if 'replicas' in d_value:
                                    _mode[d_value] = value[d_value]
                                else:
                                    _mode[d_value] = value[d_value]

                            #TODO: (NJT) Need to sort this out, better with the TAsk Template
                            # if 'placement' in d_value:
                            #     placement_spec = docker.types.Placement(
                            #         **value[d_value])
                            #     print(placement_spec)

                            if 'resources' in d_value:
                                resource_spec = DockerClient.parse_resources(
                                    value, d_value)
                                _service_spec['resources'] = resource_spec

                        # Setting the types
                        mode_spec = docker.types.ServiceMode(**_mode)
                        _service_spec['mode'] = mode_spec

                    else:
                        if 'networks' in key:
                            for n_key, n_value in s_config['networks'].items():
                                for k, v in n_value.items():
                                    if 'name' in k:
                                        networks.append(v)
                            _service_spec['networks'] = networks
                        else:
                            _service_spec[key] = value
        yield _service_spec

        # Creating Service
        #self._client.services.create(**service_spec)

    ###########################################################################
    # Methods
    ###########################################################################

    @staticmethod
    def parse_resources(value, d_value):
        """ Parse resources key
        Rename the key
        Return resources_spec

        Args:
            value
            d_value
        """

        # Initialising empty dictionary
        _resources = {}

        for r in value[d_value]:
            if 'limits' in r:
                #TODO:(NJT) Need to check if there is a better way to do this
                for r_key, r_value in value[d_value][r].items():
                    if 'cpu' in r_key:
                        cpu_value = float(r_value) * 10**9
                        cpu_key = r_key[:3] + '_limit'
                        _resources[cpu_key] = int(cpu_value)
                    if 'mem' in r_key:
                        mem_value = re.sub('M', '', r_value)
                        mem_key = r_key[:3] + '_limit'
                        _resources[mem_key] = int(mem_value)*1048576
        _resource_spec = docker.types.Resources(**_resources)
        return _resource_spec

    # def create_task_template(self, value):
    #     """" Create task template which can be used when creating or updaing
    #     a service
    #     """
    #
    #     for d_value in value:
    #         print(d_value)
    #         if 'resources' in d_value:
    #             print("In HERE")
    #             resource_spec = DockerClient.parse_resources(value, d_value)
    #
    #         #     service_spec[
    #         #         'resources'] = resource_spec
    #         # print(deploy_value)
    #         #
    #         # if 'placement' in deploy_value:
    #         #     for p_key in value[deploy_value]:
    #         #         # service_spec[p_key] = value[deploy_value][p_key]
    #         #     # print()
    #         #     # for p_key in value[deploy_value]:
    #         #     #     print(value[deploy_value][p_key])
    #
    #         print(d_value)
    #         if 'restart_policy' in d_value:
    #             for r_value in value:
    #                 print(value[r_value])
    #         #         r_new = value[r_value]
    #         #         print(r_new)
    #         #         restart_spec = docker.types.RestartPolicy(**r_new)
    #         #         print(restart_spec)
    #
    #         # else:
    #         #     mode[deploy_value] = value[deploy_value]
    #         #     mode_spec = docker.types.ServiceMode(**mode)
    #         #     service_spec['mode'] = mode_spec
    #
    #         return 0


    # DONT DELETE NOW, USEFUL CODE
    # def print_keyword_args(self, **kwargs):
    #     list = []
    #     # kwargs is a dict of the keyword args passed to the function
    #     for key, value in kwargs.items():
    #         print("%s = %s" % (key, value))
    #         list.append("%s = %s" % (key, value))

