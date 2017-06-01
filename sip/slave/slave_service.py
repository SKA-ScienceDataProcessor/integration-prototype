# -*- coding=utf-8 -*-
"""rpyc server interface for a slave controller."""
import os
import threading
import time

import rpyc

from sip.common.logging_api import log
from sip.slave import config


class SlaveService(rpyc.Service):
    """rpyc service (server) for a slave controller."""

    def __init__(self, conn):
        """Initialise the slave service.
        """
        rpyc.Service.__init__(self, conn)

    def exposed_get_state(self):
        """Return the current slave state."""
        return config.state

    def exposed_load(self, task_description, task_control_settings):
        """Load (start) a task using the task control module."""
        config.task_control.start(task_description, task_control_settings)

    def exposed_unload(self):
        """Unload (stop) a task using the task control module."""
        config.task_control.stop()

    def exposed_shutdown(self):
        _Shutdown().start()
# Test functions
    def exposed_get_answer(self): # this is an exposed method
        return 42

    def exposed_get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"
# End test functions

class _Shutdown(threading.Thread):
    """Shutdown the slave.

    This is run in a separate thread so the that the rpc shutdown function
    can return to its caller. If we don't do this, the master controller
    hangs.
    """
    def __init__(self):
        super(_Shutdown, self).__init__()

    def run(self):
        log.info('slave exiting')

        # Give time for the rpc to return
        time.sleep(1)

        # Exit the application
        os._exit(0)
