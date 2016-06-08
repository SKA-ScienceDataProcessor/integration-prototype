""" Functions executed when the master controller is un-configured
"""
__author__ = 'David Terrett'

from docker import Client
import threading

from sip_common import logger

from sip_master.slave_map import slave_map
from sip_master import config

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

class UnConfigure(threading.Thread):
    """ Does the actual work of un-configuring the system

    Stops all the running slaves
    """
    def __init__(self):
        super(UnConfigure, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.trace('starting unconfiguration')
        for entry in slave_map:
            properties = slave_map[entry]
            if properties['state'] == 'running':
               _stop_slave(entry, properties)
        logger.trace('unconfigure done')
        config.state_machine.post_event(['unconfigure done'])
