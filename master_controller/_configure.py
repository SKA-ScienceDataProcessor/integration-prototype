""" Functions executed when the master controller is configured
"""
__author__ = 'David Terrett'

from docker import Client
import threading 

import logger

from ._HeartbeatListener import _HeartbeatListener
from ._HeartbeatListener import _heartbeat_listener
from ._slave_map import _slave_map

class _configure(threading.Thread):
    """ Does the actual work of configuring the system
    """
    def run(self):
        logger.trace('starting configuration')
        
        # Start the local telescope state
        _start_slave('lts', _slave_map['lts'])
        logger.trace('configure done')
        from .state_machine import post_event
        post_event('configure done')

def _start_slave(name, properties):
    """ Start a slave controller
    """
    if properties['type'] == 'docker':
        _start_docker_slave(name, properties)
    else:
       logger.error('failed to start "' + name + '": "' + properties['type'] +
                    '" is not a known slave type')

def _start_docker_slave(name, properties):
    """ Start a slave controller that is a Docker container
    """
    # Create a Docker client
    client = Client(version='1.21', base_url=properties['engine_url'])

    # Create a container and store its id in the properties array
    container_id = client.create_container(image=properties['image'],
                   environment={'MY_NAME':name},
                   )['Id']

    # Start it
    client.start(container_id)
    info = client.inspect_container(container_id)
    ip_address = info['NetworkSettings']['IPAddress']
    properties['address'] = ip_address
    properties['state'] = 'running'
    properties['container_id'] = container_id
    properties['timeout counter'] = properties['timeout']
    logger.info(name + ' started in container ' + container_id + ' at ' +
                ip_address)

    # Connect it to the heartbeat listener
    _heartbeat_listener.connect(ip_address)

