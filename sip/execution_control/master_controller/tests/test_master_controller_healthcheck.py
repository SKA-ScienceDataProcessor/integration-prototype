# -*- coding: utf-8 -*-
"""Test for health monitoring."""

import os

from sip_docker_swarm import DockerSwarmClient
from ..app.master_controller_healthcheck import service_health
# from ..app.health_monitoring import MasterHealthException()

DC = DockerSwarmClient()
# FILE_PATH = os.path.dirname(__file__)


def test_service_health():
    """Test the service health function"""

    service_health()


# def test_check_replica():
#     """Check if the replica monitoring is working."""
#     config_path = os.path.join(FILE_PATH, 'compose-file',
#                                'docker-compose-replica.yml')
#     with open(config_path, 'r') as compose_str:
#         s_ids = DC.create_services(compose_str)
#         assert len(s_ids) == 1
#
#
#     # check if the monitoring works
#
#
#
#     # check if an exeception is thrown
#     unittest.TestCase.assertRaises(MasterHealthException,  )
#
#     level = 0
#     while level < 1:
#         for service_id in s_ids:
#             level = DC.get_replicas(service_id)
#
#     for s_id in s_ids:
#         replicas = DC.get_replicas(s_id)
#         assert replicas == 1
#
#     # Cleaning
#     DC.delete_service("replica_test")
#     DC.delete_service("replica_test_error")
