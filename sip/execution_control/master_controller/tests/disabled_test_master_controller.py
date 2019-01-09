# -*- coding: utf-8 -*-
"""Test for master controller.

This version tests for running services within the Docker Swarm and exits
with a non-zero value should the number of replicants within a service be
zero (ie a service is not running).

"""

from sip_docker_swarm import DockerSwarmClient

DC = DockerSwarmClient()
