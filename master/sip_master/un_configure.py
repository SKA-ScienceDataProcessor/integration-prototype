""" Functions executed when the master controller is un-configured
"""
__author__ = 'David Terrett'

import rpyc
import threading
import time

from sip_common import logger

from sip_master.slave_map import slave_map
from sip_master import config

def _unload_task(name, properties):
    """ Command the slave to unload the task
    """
    conn = rpyc.connect(properties['address'], properties['rpc_port'])
    conn.root.unload()

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

    Unloads all the loaded tasks
    """
    def __init__(self):
        super(UnConfigure, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.trace('starting unconfiguration')
        for entry in slave_map:
            properties = slave_map[entry]
            if properties['state'] == 'loaded':
               _unload_task(entry, properties)
        logger.trace('unconfigure done')
        config.state_machine.post_event(['unconfigure done'])
