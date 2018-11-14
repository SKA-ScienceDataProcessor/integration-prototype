# -*- coding: utf-8 -*-
"""Test for docker client API."""

import logging
import os

from ..docker_client import DockerClient

logging.basicConfig(level=os.getenv('SIP_DOCKER_API_LOG_LEVEL', 'DEBUG'))

DC = DockerClient()
FILE_PATH = os.path.dirname(__file__)


def test_create_services():
    """Test function for create services."""
    # Passing in a test compose file
    service_names = []
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.visibility.yml')
    with open(config_path, 'r') as compose_str:
        DC.create_services(compose_str)
        service_list = DC.get_service_list()
        for services in service_list:
            names = DC.get_service_name(services)
            service_names.append(names)
        assert "recv1" in service_names

    # Cleaning
    DC.delete_service("recv1")


def test_create_start_stage():
    service_names = []
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.workflow.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)

        for service_id in s_ids:
            service_details = DC.get_service_details(service_id)
            print(service_details['Spec']['Name'])
            service_names.append(service_details['Spec']['Name'])
        assert "start_stage" in service_names

    # Cleaning
    DC.delete_service("start_stage")


def test_create_volume():
    """Test function for creating volume."""
    # Create a new volume
    volume_name = 'test_volume'
    DC.create_volume(volume_name, 'local')
    assert "test_volume" in DC.get_volume_details(volume_name)['Name']

    # Cleaning
    DC.delete_volume(volume_name)
    assert "test_volume" not in DC.get_volume_list()


def test_service_state():
    """Test function to check if the service is still running."""
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.workflow.yml')
    running_service_ids = []
    test_ids = []
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        for s_id in s_ids:
            running_service_ids.append(s_id)
            test_ids.append(s_id)

    print("Service Ids: {}".format(running_service_ids))
    while running_service_ids:
        for service_id in running_service_ids:
            service_state = DC.get_service_state(service_id)
            if service_state == 'shutdown':
                DC.delete_service(service_id)
                print("Service Deleted")
                running_service_ids.remove(service_id)

    # Get all service ids
    service_list = DC.get_service_list()
    for s_id in test_ids:
        assert s_id not in service_list


def test_get_service_list():
    """Test function for getting service list."""
    # Create new services
    service_names = []
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.yml')
    DC.create_services(config_path)
    service_list = DC.get_service_list()
    for services in service_list:
        names = DC.get_service_name(services)
        service_names.append(names)
    assert "config_database" in service_names
    assert "config_database1" in service_names
    assert "config_database2" in service_names

    # Create more services
    config_path_ = os.path.join(FILE_PATH, '..', 'compose-file',
                                'docker-compose.shorter.yml')
    DC.create_services(config_path_)
    more_service_list = DC.get_service_list()
    for services in more_service_list:
        names = DC.get_service_name(services)
        if names not in service_names:
            service_names.append(names)
    assert "scheduler1" in service_names
    assert "scheduler2" in service_names

    # Cleaning
    for services in service_names:
        DC.delete_service(services)


def test_get_node_list():
    """Test function for getting nodes list."""
    # Number of nodes
    assert len(DC.get_node_list()) == 1


def test_get_volume_list():
    """Test function for getting volume list."""
    # Create a new volume
    volume_name = 'test_volume'
    DC.create_volume(volume_name, 'local')
    assert "test_volume" in DC.get_volume_details(volume_name)['Name']

    # Try with a invalid name
    assert 'invalid_name' not in DC.get_volume_list()

    # Cleaning
    DC.delete_volume(volume_name)
    assert volume_name not in DC.get_volume_list()


def test_delete_service():
    """Test function for deleting a service."""
    # Passing in a test compose file
    service_names = []
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.visibility.yml')
    DC.create_services(config_path)
    DC.delete_service("recv1")

    service_list = DC.get_service_list()
    for services in service_list:
        names = DC.get_service_name(services)
        service_names.append(names)
    assert "recv1" not in service_names


def test_delete_volume():
    """Test function for deleting a volume."""
    # Create a new volume
    DC.create_volume('delete_volume', 'local')

    DC.delete_volume('delete_volume')
    assert "delete_volume" not in DC.get_volume_list()
