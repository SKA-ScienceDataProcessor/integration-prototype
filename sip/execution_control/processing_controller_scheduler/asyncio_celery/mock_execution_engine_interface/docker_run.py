# -*- coding: utf-8 -*-
"""Mock Docker engine interface library module.

This module provides a set of functions needed to run Docker container workflow
tasks using a the local docker engine (Not in Swarm Mode)
from the Processing Block Controller.
"""

import docker


class DockerRun:

    def __init__(self):
        self._client = docker.from_env()
        self._container = None

    def run(self):
        """Runs a Docker Container"""
        # https://docker-py.readthedocs.io/en/stable/containers.html
        self._container = self._client.containers.run(
            image='skasip/mock_workflow_task_01',
            command='{}',
            detach=True,
            auto_remove=True)
        # print(_container.logs())

    def stop(self):
        pass

    def info(self):
        pass
