# -*- coding: utf-8 -*-
"""Mock Docker engine interface library module.

This module provides a set of functions needed to run Docker container workflow
tasks using a the local docker engine (Not in Swarm Mode)
from the Processing Block Controller.

"""

import docker
import logging
LOG = logging.getLogger('sip.docker_run')


class RunDockerContainer:
    """Class Representing a docker container task running on the local docker
       engine"""

    def __init__(self):
        self._client = docker.from_env()
        # print(self._client.version())
        self._container = None
        # self._client.containers.list(all=True)

    def __del__(self):
        LOG.info('Waiting for container to exit..')
        self._container.wait(timeout=20)
        self._container.kill()

    def run(self, image, command, detach=True, auto_remove=True):
        """Runs a Docker Container"""
        LOG.info('Running container: %s', image)
        # https://docker-py.readthedocs.io/en/stable/containers.html
        self._container = self._client.containers.run(
            image=image,
            command=command,
            detach=detach,
            auto_remove=auto_remove
        )
        # code = self._container.wait()
        # print(_container.logs())

    def wait(self, timeout=10):
        """Wait for the container to finish"""
        self._container.wait(timeout=timeout)

    def stop(self):
        self._container.stop(timeout=3)

    def kill(self):
        LOG.info('Killing Container')
        self._container.kill()

    def info(self):
        # print(self._container.status())
        # print(self._container.stats())
        _client = docker.APIClient()
        # print('---')
        # print(_client.version())
        # print('---')
        # print(type(_client))
        # print('---')
        info = _client.inspect_container(self._container.id)
        # print(info['State'])
        return info


