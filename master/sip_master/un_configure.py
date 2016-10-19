""" Functions executed when the master controller is un-configured
"""
__author__ = 'David Terrett'

import rpyc
import threading
import time

from sip_common import logger

from sip_master import config
from sip_master import task_control

class UnConfigure(threading.Thread):
    """ Does the actual work of un-configuring the system

    Unloads all the loaded tasks
    """
    def __init__(self):
        super(UnConfigure, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.info('starting unconfiguration')
        for slave, status in config.slave_status.items():
            if status['state'].current_state() == 'Busy':
               type = status['type']
               task_control.unload(config.slave_config[type], status)
        logger.info('unconfigure done')
