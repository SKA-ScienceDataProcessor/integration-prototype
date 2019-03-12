# -*- coding: utf-8 -*-
"""Experimental Docker Compose API."""
import os
import logging

import docker


LOG = logging.getLogger('sip.ee.docker.stack')


class Stack:

    def __init__(self):
        self._client = docker.from_env()

    def list(self):
        """Get list of docker stack."""
        # services = self._client.services.list()
        print(self._client.version())
        # print(self._client.swarm.id)
        print(self._client.services(filters=None))
        # print(self._client.inspect_swarm())
        # print(self._client.nodes())
        return []
        # return services

    def deploy(self, file):
        pass

    def remove(self, id):
        pass

    def services(self, id):
        pass
