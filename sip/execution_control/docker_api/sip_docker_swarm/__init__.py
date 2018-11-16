# coding=utf-8
"""SIP Docker Swarm client library."""
from .docker_client import DockerClient
from .version import __version__
__all__ = ['DockerClient', '__version__']
