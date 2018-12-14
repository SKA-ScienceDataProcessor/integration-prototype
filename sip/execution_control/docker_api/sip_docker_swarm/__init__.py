# coding=utf-8
"""SIP Docker Swarm client library."""
from .docker_swarm_client import DockerSwarmClient
from .version import __version__
__all__ = ['DockerSwarmClient', '__version__']
