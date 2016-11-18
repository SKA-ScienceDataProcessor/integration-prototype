# -*- coding=utf-8 -*-
"""rpyc server interface for a slave controller."""
import importlib
import os
import threading
import time

import rpyc

from sip_common import logger
from sip_slave import config


class SlaveService(rpyc.Service):
    """rpyc service (server) for a slave controller."""

    def __init__(self, conn):
        """Initialise the slave service with the task control module.

        The task control module to use is specified in the slave map JSON
        settings file read by the master controller main() and currently
        stored in the slave global variable: config.task_control_module
        """
        rpyc.Service.__init__(self, conn)
        _class = getattr(importlib.import_module('sip_slave.task_control'),
                         config.task_control_module)
        self.task_control = _class()

    def exposed_get_state(self):
        """Return the current slave state."""
        return config.state

    def exposed_load(self, task_description):
        """Load (start) a task using the task control module."""
        self.task_control.start(task_description)

    def exposed_unload(self, task_description):
        """Unload (stop) a task using the task control module."""
        self.task_control.stop(task_description)

    def exposed_shutdown(self):
        _Shutdown().start()


class _Shutdown(threading.Thread):
    """Shutdown the slave.

    This is run in a separate thread so the that the rpc shutdown function
    can return to its caller. If we don't do this, the master controller
    hangs.
    """
    def __init__(self):
        super(_Shutdown, self).__init__()

    def run(self):
        logger.info('slave exiting')

        # Give time for the rpc to return
        time.sleep(1)

        # Exit the application
        os._exit(0)
