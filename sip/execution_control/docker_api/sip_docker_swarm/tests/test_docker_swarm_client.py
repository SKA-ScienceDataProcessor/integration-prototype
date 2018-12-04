# -*- coding: utf-8 -*-
"""Test for docker client API."""

import logging
import os

from ..docker_swarm_client import DockerSwarmClient

logging.basicConfig(level=os.getenv('SIP_DOCKER_API_LOG_LEVEL', 'DEBUG'))

DC = DockerSwarmClient()
FILE_PATH = os.path.dirname(__file__)


def test_volumes():
    """Test function for getting list of volume names."""
    # Create a new volume
    volume_name = 'test_volume'
    DC.create_volume(volume_name, 'local')
    assert volume_name in DC.get_volume_details(volume_name)['Name']
    assert volume_name in DC.volume_names

    # Try with a invalid name
    assert 'invalid_name' not in DC.volume_names

    # Cleaning
    DC.delete_volume(volume_name)
    assert volume_name not in DC.volume_names


def test_services():
    """Test function for getting list of service ids."""
    # TODO(NJT)


def test_containers():
    """Test function for getting list of container ids."""
    # TODO(NJT)


def test_nodes():
    """Test function for getting list of node ids."""
    #TODO(NJT)
