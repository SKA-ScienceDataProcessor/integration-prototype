"""Setup config file to package docker swarm api."""
from setuptools import setup

setup(name='skasip-docker_swarm',
      version='1.0.0',
      description='SIP Docker Swarm client library.',
      author='SKA SIP',
      packages=['docker_client'],
      install_requires=[
          'docker'],
      zip_safe=False)
