# coding: utf-8
"""Functions executed when the master controller is shut down."""

__author__ = 'David Terrett'

import os
import signal
import threading
import time

from sip.common.logging_api import log

from sip.master.config import slave_status_dict
from sip.master import config
from sip.master import slave_control
from sip.master.slave_states import TaskStatus


class Shutdown(threading.Thread):
    """Does the actual work of shutting down the system."""

    def __init__(self):
        super(Shutdown, self).__init__()

    def run(self):
        """Thread run routine."""
        log.info('starting shutdown')

        # Shut down any slaves that are still running
        for slave, status in slave_status_dict().items():
            state = status['state'].current_state()
            print(state)
            if state != 'Exited' and state != 'Unknown':
                slave_control.stop(slave, status)

        # Shut down the log server
        log.info('Terminating logserver {}'.format(config.logserver.ident))
        config.logserver.delete()

        print('Shutdown complete. Goodbye!')

        # Give the rpc service a chance to send a reply
        time.sleep(1)
        os._exit(0)
