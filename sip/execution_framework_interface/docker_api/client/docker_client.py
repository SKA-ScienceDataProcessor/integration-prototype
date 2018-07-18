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

        # Store a flag to show whether we are on a manager node or a worker.
        self._manager = self._client.info()['Swarm']['ControlAvailable']

        # Docker low-level API
        self._api_client = docker.APIClient()

    ###########################################################################
    # Create functions
    ###########################################################################

    def create_services(self, compose_files):
        """ Create new docker services

        Args:
            compose_files (list): List of docker compose files
        """
        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be run on swarm manager nodes')

        for compose_file in compose_files:
            with open(compose_file, 'r') as file:
                try:
                    service_config = yaml.load(file)
                    for service_name in service_config['services']:
                        service_exist = self._client.services.list(
                            filters={'name': service_name})
                        if not service_exist:
                            service_spec = self.parse_service(
                                service_config, service_name)
                            for s_spec in service_spec:
                                LOG.debug('Creating services: %s', s_spec)
                                self._client.services.create(**s_spec)
                        else:
                            LOG.debug('Services already exists')

                except yaml.YAMLError as exc:
                    print(exc)

    def create_volume(self, volume_name, driver_spec=None):
        """ Create new docker volumes

        Only the manager nodes can create a volume

        Args:
            volume_name (string): Name for the new docker volume
            driver_spec (string): Driver for the docker volume
        """

        # Default values
        if driver_spec:
            driver = driver_spec
        else:
            driver = 'local'

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        self._client.volumes.create(name=volume_name, driver=driver)

    ###########################################################################
    # Delete functions
    ###########################################################################

    def delete_service(self, service_name):
        """ Removes/stops a docker service
        Only the manager nodes can delete a service

        Args:
            service_name (string): Name of the service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        # Remove service
        self._api_client.remove_service(service_name)

    def delete_all_services(self):
        """ Removes/stops a service

        Only the manager nodes can delete a service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Services can only be deleted '
                               'on swarm manager nodes')

        service_list = self.get_service_list()
        for services in service_list:
            # Remove all the services
            self._api_client.remove_service(services)

    def delete_all_volumes(self):
        """ Removes all the volumes

        Only the manager nodes can delete a volume
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Volumes can only be deleted '
                               'on swarm manager nodes')

        volume_list = self.get_volume_list()
        for volumes in volume_list:
            # Remove all the services
            self._api_client.remove_volume(volumes, force=True)

    def delete_volume(self, volume_name):
        """ Removes/stops a docker volume
        Only the manager nodes can delete a volume

        Args:
            volume_name (string): Name of the volume
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Volumes can only be deleted '
                               'on swarm manager nodes')

        # Remove volume
        self._api_client.remove_volume(volume_name)



    ###########################################################################
    # Get functions
    ###########################################################################

    def get_node_list(self):
        """ Get a list of nodes

        Only the manager nodes can retrieve all the nodes

        Returns:
            list, all the ids of the nodes in swarm
        """

        # Initialising empty list
        nodes = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node '
                               'can retrieve all the nodes.')

        node_list = self._client.nodes.list()
        for n_list in node_list:
            nodes.append(n_list.id)
        return nodes

    def get_node_details(self, node_id):
        """ Get details of a node

        Only the manager nodes can retrieve details of a node

        Args:
            node_id (list): List of node ID

        Returns:
            dict, details of the node
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can '
                               'retrieve node details.')

        node = self._client.nodes.get(node_id)
        return node.attrs

    def get_service_list(self):
        """ Get a list of docker services

        Only the manager nodes can retrieve all the services

        Returns:
            list, all the ids of the services in swarm
        """

        # # Initialising empty list
        services = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve'
                               ' all the services.')

        service_list = self._client.services.list()
        for s_list in service_list:
            services.append(s_list.id)
        return services

    def get_service_details(self, service_id):
        """ Get details of a service

        Args:
            service_id (string): List of service ID

        Returns:
            dict, details of the service
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve all'
                               ' the services details.')

        service = self._client.services.get(service_id)
        return service.attrs

    def get_volume_list(self):
        """ Get a list of docker volumes

        Only the manager nodes can retrieve all the volumes

        Returns:
            list, all the names of the volumes in swarm
        """
        volumes = []

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can retrieve'
                               ' all the services.')

        volume_list = self._client.volumes.list()
        for v_list in volume_list:
            volumes.append(v_list.name)
        return volumes

    def get_volume_details(self, volume_name):
        """ Get details of the volume

        Args:
            volume_name (string): Name of the volume

        Returns:
            dict, details of the volume
        """

        if volume_name not in self.get_volume_list():
            raise RuntimeError('No such volume found: ', volume_name)

        volume = self._client.volumes.get(volume_name)
        return volume.attrs

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_labels(self, node_name, labels):
        """Update label of a node

          Args:
            node_name (string): Name of the node.
            labels (dict): Label to add to the node
        """

        # Raise an exception if we are not a manager
        if not self._manager:
            raise RuntimeError('Only the Swarm manager node can update '
                               'node details.')

        # Node specification
        node_spec = {'Availability': 'active',
                     'Name': node_name,
                     'Role': 'manager',
                     'Labels': labels
                     }

        node = self._client.nodes.get(node_name)
        node.update(node_spec)

    ###########################################################################
    # Parsing functions
    ###########################################################################

    @staticmethod
    def parse_service(service_config, service_name):
        """Parsing the docker compose file

        Args:
            service_config (dict): Service configurations from the compose file
            service_name (string): Name of the services

        Returns:
            dict, service specifications extracted from the compose file
        """
        # Initialising empty dictionary and list
        service_spec = {}
        endpoints = {}
        mode = {}
        networks = []

        service_spec['name'] = service_name
        for key, value in service_config['services'][service_name].items():
            if 'ports' in key:
                for port_element in value:
                    target_port = port_element.split(':')
                    for port in target_port:
                        endpoints[int(port)] = int(port)

                # Setting the types
                endpoint_spec = docker.types.EndpointSpec(ports=endpoints)
                service_spec['endpoint_spec'] = endpoint_spec
            else:
                if 'volumes' in key:
                    for v_values in value:
                        for v_key, v_value in v_values.items():
                            if v_key == 'source':
                                if v_value == '.':
                                    source = os.path.dirname(
                                        os.path.abspath(__file__))
                                else:
                                    source = v_value
                            if v_key == 'target':
                                target = v_value
                        volume = [source + ':' + target]
                        service_spec['mounts'] = volume
                else:
                    if 'deploy' in key:
                        for d_value in value:
                            if 'restart_policy' in d_value:
                                restart_spec = docker.types.RestartPolicy(
                                    **value[d_value])
                                service_spec['restart_policy'] = restart_spec
                            if 'mode' in d_value:
                                if 'replicas' in d_value:
                                    mode[d_value] = value[d_value]
                                else:
                                    mode[d_value] = value[d_value]
                            if 'resources' in d_value:
                                resource_spec = DockerClient.parse_resources(
                                    value, d_value)
                                service_spec['resources'] = resource_spec

                        # Setting the types
                        mode_spec = docker.types.ServiceMode(**mode)
                        service_spec['mode'] = mode_spec
                    else:
                        if 'networks' in key:
                            for n_key, n_value in \
                                    service_config['networks'].items():
                                for n_key_, n_value_ in n_value.items():
                                    if 'name' in n_key_:
                                        networks.append(n_value_)
                            service_spec['networks'] = networks
                        else:
                            service_spec[key] = value
        yield service_spec

    @staticmethod
    def parse_resources(value, deploy_value):
        """ Parse resources key
        Rename the key
        Return resources_spec

        Args:
            value (dict): Resource configurations
            deploy_value (string): Resource name

        Returns:
            dict, resources specification
        """

        # Initialising empty dictionary
        resources = {}

        for resource_values in value[deploy_value]:
            if 'limits' in resource_values:
                for r_key, r_value in value[deploy_value][resource_values].items():
                    if 'cpu' in r_key:
                        cpu_value = float(r_value) * 10**9
                        cpu_key = r_key[:3] + '_limit'
                        resources[cpu_key] = int(cpu_value)
                    if 'mem' in r_key:
                        mem_value = re.sub('M', '', r_value)
                        mem_key = r_key[:3] + '_limit'
                        resources[mem_key] = int(mem_value)*1048576
        resources_spec = docker.types.Resources(**resources)
        return resources_spec
