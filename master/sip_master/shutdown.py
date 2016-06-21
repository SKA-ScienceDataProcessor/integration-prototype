""" Functions executed when the master controller is shut down
"""
__author__ = 'David Terrett'

from docker import Client
import rpyc
import os
import threading

from sip_common import logger

from sip_master import config

def _stop_slave(name, config, status):
    """ Stop a slave controller
    """
    conn = rpyc.connect(status['address'], config['rpc_port'])
    conn.root.shutdown()
    if config['type'] == 'docker':
        _stop_docker_slave(name, config, status)
    else:
       logger.error('failed to stop "' + name + '": "' + config['type'] +
                    '" is not a known slave type')


def _stop_docker_slave(name, config, status):
    """ Stop a docker based slave controller
    """

    # Create a Docker client
    client = Client(version='1.21', base_url=config['engine_url'])

    # Stop the container and remove the container
    client.stop(status['container_id'])
    client.remove_container(status['container_id'])

    # Clear the status in the property map
    status['state'] = ''

class Shutdown(threading.Thread):
    """ Does the actual work of shutting down the system
    """
    def __init__(self):
        super(Shutdown, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.trace('starting shutdown')
        for slave, status in config.slave_status.items():

            # If the slave is running tell it to shut down
            if status['state'] != '' and status['state'] != 'dead':
                _stop_slave(slave, config.slave_config[slave], status)
        logger.trace('shutdown done')
        os._exit(0)
