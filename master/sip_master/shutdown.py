""" Functions executed when the master controller is shut down
"""
__author__ = 'David Terrett'

from docker import Client
import rpyc
import os
import threading

from sip_common import logger

from sip_master.slave_map import slave_map
from sip_master import config

def _stop_slave(name, properties):
    """ Stop a slave controller
    """
    conn = rpyc.connect(properties['address'], properties['rpc_port'])
    conn.root.shutdown()
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

    # Stop the container and remove the container
    client.stop(properties['container_id'])
    client.remove_container(properties['container_id'])

    # Clear the status in the property map
    properties['state'] = ''

class Shutdown(threading.Thread):
    """ Does the actual work of shutting down the system
    """
    def __init__(self):
        super(Shutdown, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.trace('starting shutdown')
        for entry in slave_map:
            properties = slave_map[entry]

            # If the slave is running tell it to shut down
            if properties['state'] == 'running':
                _stop_slave(entry, properties)
        logger.trace('shutdown done')
        os._exit(0)
