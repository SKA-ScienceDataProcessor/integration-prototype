# -*- coding: utf-8 -*-
"""Test for docker client API"""

import logging
import time

from ..docker_client import DockerClient

logging.basicConfig(level='DEBUG')

DC = DockerClient()


def test_create_services():
    """ Test function for create services"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Passing in a test compose file
    filename = ["compose-file/docker-compose.visibility.yml"]
    DC.create_services(filename)
    assert len(DC.get_service_list()) == 1


def test_create_volume():
    """ Test function for creating volume"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new volume
    DC.create_volume('test_volume', 'local')
    assert len(DC.get_volume_list()) == 1


def test_get_service_list():
    """ Test function for getting service list"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new service
    compose_file = ["compose-file/docker-compose.visibility.yml"]
    DC.create_services(compose_file)
    assert len(DC.get_service_list()) == 1

    # Add more services
    more_file = ["compose-file/docker-compose.yml"]
    DC.create_services(more_file)
    assert len(DC.get_service_list()) == 4

    # Create a service with list of files
    compose_files = ["compose-file/docker-compose.hostnet.yml",
                     "compose-file/docker-compose.shorter.yml"]
    DC.create_services(compose_files)
    assert len(DC.get_service_list()) == 8


def test_get_node_list():
    """ Test function for getting nodes list"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Number of nodes
    assert len(DC.get_node_list()) == 1


def test_get_volume_list():
    """ Test function for getting volume list"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new volume
    DC.create_volume('test_volume', 'local')
    assert len(DC.get_volume_list()) == 1

    # Try with a invalid name
    assert 'invalid_name' not in DC.get_volume_list()


def test_delete_service():
    """ Test function for deleting a service"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Passing in a test compose file
    filename = ["compose-file/docker-compose.visibility.yml"]
    DC.create_services(filename)
    assert len(DC.get_service_list()) == 1

    DC.delete_service("recv1")
    assert len(DC.get_service_list()) < 1


def test_delete_volume():
    """ Test function for deleting a volume"""

    # Remove all services and volumes
    DC.delete_all_services()
    assert not DC.get_service_list()
    time.sleep(2)
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new volume
    DC.create_volume('delete_volume', 'local')
    assert len(DC.get_volume_list()) == 1

    DC.delete_volume('delete_volume')
    assert "delete_volume" not in DC.get_volume_list()


# def test_quick_test():
#
#     # Create a service with list of files
#     compose_files = ["compose-file/docker-compose.visibility.yml",
#                      "compose-file/docker-compose.shorter.yml",
#                      "compose-file/docker-compose.hostnet.yml",
#                      "compose-file/vis_receive_example.yml",
#                      "compose-file/docker-compose.yml"]
#     DC.create_services(compose_files)
