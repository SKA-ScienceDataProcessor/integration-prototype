# -*- coding: utf-8 -*-
"""Test for health monitoring."""

import os
import time
from sip_docker_swarm import DockerSwarmClient
from ..master_controller_healthcheck import MasterHealthCheck


DC = DockerSwarmClient()
MHC = MasterHealthCheck()
FILE_PATH = os.path.dirname(__file__)


def test_get_services_health():
    """Test the service health function"""
    # Initialise
    service_names = []

    config_path = os.path.join(FILE_PATH, 'compose-file',
                               'docker-compose-services.yml')
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        assert len(s_ids) == 2

    for s_id in s_ids:
        service_names.append(DC.get_service_name(s_id))

    assert 'service_health' in service_names
    assert 'service_health_error' in service_names

    time.sleep(10)
    s_heath = MHC.services_health
    assert s_heath['service_health'] == "Healthy"
    assert s_heath['service_health_error'] == "Unhealthy"

    # Cleaning
    DC.delete_service("service_health")
    DC.delete_service("service_health_error")


def test_get_service_health():
    """Test the service health by service id."""
    config_path = os.path.join(FILE_PATH, 'compose-file',
                               'docker-compose-service.yml')
    with open(config_path, 'r') as compose_str:
        s_id = DC.create_services(compose_str)
        assert len(s_id) == 1

    time.sleep(10)
    assert MHC.get_service_health(s_id[0]) == "Healthy"

    # Cleaning
    DC.delete_service("service_health")


def test_get_overall_services_health():
    """Test the overall service health function. """
    config_path = os.path.join(FILE_PATH, 'compose-file',
                               'docker-compose-overall.yml')
    with open(config_path, 'r') as compose_str:
        s_id = DC.create_services(compose_str)
        assert len(s_id) == 2

    time.sleep(10)
    assert MHC.overall_health == "Healthy"

    # Cleaning
    DC.delete_service("service_health_1")
    DC.delete_service("service_health_2")

    config_path = os.path.join(FILE_PATH, 'compose-file',
                               'docker-compose-services.yml')
    with open(config_path, 'r') as compose_str:
        s_id = DC.create_services(compose_str)
        assert len(s_id) == 2

    time.sleep(5)
    assert MHC.overall_health == "Unhealthy"

    # Cleaning
    DC.delete_service("service_health")
    DC.delete_service("service_health_error")
