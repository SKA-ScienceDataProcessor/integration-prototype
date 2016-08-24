""" Functions executed when the master controller is shut down
"""
__author__ = 'David Terrett'

from docker import Client
import rpyc
import os
import threading

from sip_common import logger

from sip_master import config
from sip_master import slave_control

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
            if status['expected_state'] != '' and (
                    status['state'] != 'dead') and (
                    status['state'] != 'finished'):
                slave_control.stop(slave, status)
        logger.trace('shutdown done')
        os._exit(0)
