""" Functions executed when the master controller is un-configured
"""
__author__ = 'David Terrett'

from docker import Client
import threading

import logger

from ._slave_map import _slave_map

def _stop_slave(name, properties):
    """ Stop a slave controller
    """
    if properties['type'] == 'docker':
        _stop_docker_slave(name, properties)
    else:
       logger.error('failed to stop "' + name + '": "' + properties['type'] +
                    '" is not a known slave type')

def _stop_docker_slave(name, properties):
    """ Stop a docker based slave controller
    """

    # Create a Docker client
    client = Client(version='1.21', base_url=properties['engine_url'])

    # Stop the container
    client.stop(properties['container_id'])

    # Clear the status in the property map
    properties['state'] = ''

class _unconfigure(threading.Thread):
    """ Does the actual work of un-configuring the system

    Stops all the running slaves
    """
    def __init__(self, mc):
        """ Stores the state machine

        The state machine is needed so that we can post an "unconfigure done"
        event when the system is unconfigured.
        """
        self._mc = mc
        super(_unconfigure, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.trace('starting unconfiguration')
        for entry in _slave_map:
            properties = _slave_map[entry]
            if properties['state'] == 'running':
               _stop_slave(entry, properties)
        logger.trace('unconfigure done')
        self._mc.post_event(['unconfigure done'])
