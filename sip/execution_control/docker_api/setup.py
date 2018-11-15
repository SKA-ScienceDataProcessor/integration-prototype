"""Setup config file to package docker swarm api."""
from setuptools import setup
import docker_client


with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()


VERSION = docker_client.__version__


setup(name='skasip-docker_swarm',
      version=VERSION,
      author='SKA SDP SIP team.',
      description='SIP Docker Swarm client library.',
      long_description=LONG_DESCRIPTION,
      url='https://github.com/SKA-ScienceDataProcessor/integration-prototype'
          '/tree/master/sip/execution_control/docker_swarm_api',
      packages=['docker_client'],
      install_requires=[
          'docker'
      ],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: BSD License"
      ]
      )
