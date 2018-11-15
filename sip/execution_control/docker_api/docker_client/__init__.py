# coding=utf-8
"""SIP Docker Swarm client library."""
from .docker_client import DockerClient
__version_info__ = (1, 0, 0)
__version__ = '.'.join(map(str, __version_info__))
__all__ = ['DockerClient']
