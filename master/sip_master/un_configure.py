""" Functions executed when the master controller is un-configured
"""
__author__ = 'David Terrett'

import rpyc
import threading
import time

from sip_common import logger

from sip_master.slave_map import slave_config
from sip_master.slave_map import slave_status
from sip_master import config

def _unload_task(slave, cfg, status):
    """ Command the slave to unload the task
    """
    conn = rpyc.connect(status['address'], cfg['rpc_port'])
    conn.root.unload()

def _stop_docker_slave(slave, cfg, status):
    """ Stop a docker based slave controller
    """

    # Create a Docker client
    client = Client(version='1.21', base_url=cfg['engine_url'])

    # Stop the container
    client.stop(status['container_id'])

    # Clear the status in the property map
    status['state'] = ''

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
        for slave, status in slave_status.items():
            if status['state'] == 'busy':
               _unload_task(slave, slave_config[slave], status)
        logger.trace('unconfigure done')
        config.state_machine.post_event(['unconfigure done'])
