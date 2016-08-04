""" Functions executed when the master controller is un-configured
"""
__author__ = 'David Terrett'

import rpyc
import threading
import time

from sip_common import logger

from sip_master import config
from sip_master import task

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
        for slave, status in config.slave_status.items():
            if status['state'] == 'busy':
               task.unload(config.slave_config[slave], status)
        logger.trace('unconfigure done')
        config.state_machine.post_event(['unconfigure done'])
