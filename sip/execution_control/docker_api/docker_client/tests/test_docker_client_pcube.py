# -*- coding: utf-8 -*-
"""Test for docker client API on P3."""

import logging
import os

from ..docker_client import DockerClient

logging.basicConfig(level=os.getenv('SIP_DOCKER_API_LOG_LEVEL', 'DEBUG'))

DC = DockerClient()
FILE_PATH = os.path.dirname(__file__)


def test_log_driver():
    """Test function to check if log driver is loaded correctly from
    compose file.

    """
    config_path = os.path.join(FILE_PATH, '..', 'compose-file',
                               'docker-compose.p3-fluentd.yml')
    running_service_ids = []
    test_ids = []
    with open(config_path, 'r') as compose_str:
        s_ids = DC.create_services(compose_str)
        # TODO (NJT) nEED TO COMPLETE THIS UNIT TEST
        # GET SERVICE DETAILS AND GET THE LOG DRIVE AND LOG OPTIONS FROM IT
        for s_id in s_ids:
            running_service_ids.append(s_id)
            test_ids.append(s_id)

    # Cleaning
    DC.delete_service("workflow_stage_1_a")
    DC.delete_service("workflow_stage_1_b")
