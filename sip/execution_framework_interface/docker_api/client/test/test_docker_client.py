# -*- coding: utf-8 -*-
"""Test for docker client API"""

import logging

from ..docker_client import DockerClient

logging.basicConfig(level='DEBUG')

DC = DockerClient()


def test_create_service():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Passing in a test compose file
    filename = ["compose-file/docker-compose.visibility.yml"]
    DC.create_services(filename)
    assert len(DC.get_service_list()) == 1


def test_create_volume():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Remove all the volumes
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new volume
    DC.create_volume('test_volume', 'local')
    assert len(DC.get_volume_list()) == 1


def test_get_service_list():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Remove all the volumes
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

    # Remove one service
    DC.delete_service("recv1")
    assert len(DC.get_service_list()) == 3

    # # Delete a service with invalid name
    # DC.delete_service("r1")
    # DC.create_services(compose_file)
    # assert len(DC.get_service_list()) == 3
    # TODO: (NJT) Need to check and add runtime error
    #
    # # Create a service with invalid compose file
    # invalid_file = ["compose-file/invalid-compose.yml"]
    # DC.create_services(invalid_file)
    # assert len(DC.get_service_list()) == 3
    # TODO: (NJT) Need to check and add runtime error

    # Create a service with list of files
    compose_files = ["compose-file/docker-compose.hostnet.yml",
                     "compose-file/docker-compose.shorter.yml"]
    DC.create_services(compose_files)
    assert len(DC.get_service_list()) == 7


def test_get_nodes_list():

    # Number of nodes
    assert len(DC.get_node_list()) == 1


def test_get_volume_list():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Remove all the volumes
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new volume
    DC.create_volume('test_volume', 'local')
    assert len(DC.get_volume_list()) == 1

    # Try with a invalid name
    assert 'invalid_name' not in DC.get_volume_list()


def test_delete_service():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Passing in a test compose file
    filename = ["compose-file/docker-compose.visibility.yml"]
    DC.create_services(filename)
    assert len(DC.get_service_list()) == 1

    DC.delete_service("recv1")
    assert "recv1" not in DC.get_service_list()


def test_delete_all_services():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()


def test_delete_volume():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Remove all the volumes
    DC.delete_all_volumes()
    assert not DC.get_volume_list()

    # Create a new volume
    DC.create_volume('delete_volume', 'local')
    assert len(DC.get_volume_list()) == 1

    DC.delete_volume('delete_volume')
    assert "delete_volume" not in DC.get_volume_list()


def test_delete_all_volumes():

    # Remove all the services
    DC.delete_all_services()
    assert not DC.get_service_list()

    # Remove all the volumes
    DC.delete_all_volumes()
    assert not DC.get_volume_list()
