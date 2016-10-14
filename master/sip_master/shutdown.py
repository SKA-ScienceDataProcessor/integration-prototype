""" Functions executed when the master controller is shut down
"""
__author__ = 'David Terrett'

from docker import Client
import rpyc
import os
import signal
import threading
import time

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
        logger.info('starting shutdown')

        # Shut down any slaves that are still running
        for slave, status in config.slave_status.items():
            if status['expected_state'] != '' and (
                    status['state'] != 'dead') and (
                    status['state'] != 'finished'):
                slave_control.stop(slave, status)

        # Shut down the log server
        print('Terminating logserver, pid ', config.logserver.pid)
        os.kill(config.logserver.pid, signal.SIGTERM)

        logger.info('shutdown done')

        # Give the rpc service a change to send a reply
        time.sleep(1)
        os._exit(0)
