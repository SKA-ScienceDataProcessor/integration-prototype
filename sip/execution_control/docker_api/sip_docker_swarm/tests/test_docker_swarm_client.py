# -*- coding: utf-8 -*-
"""Test for docker client API."""

import os

from ..docker_swarm_client import DockerSwarmClient
DC = DockerSwarmClient()
FILE_PATH = os.path.dirname(__file__)


def test_volumes():
    """Test function for getting list of volume names."""
    # Create a new volume
    volume_name = 'test_volume'
    DC.create_volume(volume_name, 'local')
    assert volume_name in DC.get_volume_details(volume_name)['Name']
    assert volume_name in DC.volumes

    # Try with a invalid name
    assert 'invalid_name' not in DC.volumes

    # Cleaning
    DC.delete_volume(volume_name)
    assert volume_name not in DC.volumes


def test_services():
    """Test function for getting list of service ids."""
    # Create new services
    service_names = []
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.shorter.yml')
    with open(config_path, 'r') as compose_str:
        service_ids = DC.create_services(compose_str)
        for service_id in service_ids:
            service_list = DC.get_service_list()
            assert service_id in service_list

        service_list = DC.services
        for services in service_list:
            names = DC.get_service_name(services)
            service_names.append(names)
        assert "scheduler1" in service_names
        assert "scheduler2" in service_names

    # Cleaning
    DC.delete_service("scheduler1")
    DC.delete_service("scheduler2")

# def test_containers():
#     """Test function for getting list of container ids."""
#     # TODO(NJT)
#     # Passing in a test compose file
#     service_names = []
#     config_path = os.path.join(FILE_PATH, '..', 'compose-file',
#                                'docker-compose.p3-fluentd.yml')
#     with open(config_path, 'r') as compose_str:
#         s_ids = DC.create_services(compose_str)
#
#         for service_id in s_ids:
#             service_details = DC.get_service_details(service_id)
#
#         # TODO (NJT) Need a real container to test this
#         print("Containers {}".format(DC.containers))
#     #         service_names.append(service_details['Spec']['Name'])
#     #     assert "recv" in service_names
#     #     assert "send" in service_names
#     #
#     # Cleaning
#     DC.delete_service("recv")
#     DC.delete_service("send")


def test_nodes():
    """Test function for getting list of node ids."""

    # Number of nodes
    assert len(DC.nodes) == 1


def test_create_services():
    """Test function for create services."""
    # Passing in a test compose file
    service_names = []
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose-run-local.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        for service_id in s_ids:
            service_details = DC.get_service_details(service_id)
            service_names.append(service_details['Spec']['Name'])
        assert "recv" in service_names
        assert "send" in service_names

    # Cleaning
    DC.delete_service("recv")
    DC.delete_service("send")


def test_create_volume():
    """Test function for creating volume."""
    # Create a new volume
    volume_name = 'test_volume'
    DC.create_volume(volume_name, 'local')
    assert "test_volume" in DC.get_volume_details(volume_name)['Name']

    # Cleaning
    DC.delete_volume(volume_name)
    assert "test_volume" not in DC.get_volume_list()


def test_workflow_and_service_state():
    """Test function to to start workflow and check if the service is
    running and shutdown at the right time. """
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.workflow.yml')
    service_names = []
    running_service_ids = []
    test_ids = []
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        for s_id in s_ids:
            service_details = DC.get_service_details(s_id)
            service_names.append(service_details['Spec']['Name'])
            running_service_ids.append(s_id)
            test_ids.append(s_id)
        assert "start_stage" in service_names
        assert "mock_stage" in service_names
        assert "mock_workflow_stage1" in service_names

    while running_service_ids:
        for service_id in running_service_ids:
            service_state = DC.get_service_state(service_id)
            if service_state == 'shutdown':
                DC.delete_service(service_id)
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
                               'docker-compose.shorter.yml')
    with open(config_path, 'r') as compose_str:
        service_ids = DC.create_services(compose_str)
        for service_id in service_ids:
            service_list = DC.get_service_list()
            assert service_id in service_list

        service_list = DC.get_service_list()
        for services in service_list:
            names = DC.get_service_name(services)
            service_names.append(names)
        assert "scheduler1" in service_names
        assert "scheduler2" in service_names

    # Cleaning
    DC.delete_service("scheduler1")
    DC.delete_service("scheduler2")


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
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.visibility.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        for service_id in s_ids:
            DC.delete_service(service_id)
            service_list = DC.get_service_list()
            assert service_id not in service_list


def test_delete_volume():
    """Test function for deleting a volume."""
    # Create a new volume
    DC.create_volume('delete_volume', 'local')

    DC.delete_volume('delete_volume')
    assert "delete_volume" not in DC.get_volume_list()


def test_replication_level():
    """Test function for getting the replication level of a service."""
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose-replica.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        assert len(s_ids) == 1

    level = 0
    while level < 1:
        for service_id in s_ids:
            level = DC.get_replicas(service_id)

    for s_id in s_ids:
        replicas = DC.get_replicas(s_id)
        assert replicas == 1

    # Cleaning
    DC.delete_service("replica_test")


def test_actual_replica_level():
    """Test function for getting the actual replica level of a service."""
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose-replica.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        assert len(s_ids) == 1

    for service_id in s_ids:
        level = DC.get_actual_replica(service_id)
        assert level == 1

    # Cleaning
    DC.delete_service("replica_test")


def test_environment():
    """Test function for setting environment variables."""
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose-env.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        assert len(s_ids) == 1

    level = 0
    while level < 1:
        for service_id in s_ids:
            level = DC.get_replicas(service_id)

    for s_id in s_ids:
        replicas = DC.get_replicas(s_id)
        assert replicas == 1

    # Cleaning
    DC.delete_service("process_data")
