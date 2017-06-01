#!/usr/bin/python3
"""Skeleton slave controller.

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

import importlib
import os
import signal
import sys
import threading
import time
from rpyc.utils.server import ThreadedServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sip.common.logging_api import log
from sip.common import heartbeat
from sip.slave import config

def _sig_handler(signum, frame):
    sys.exit(0)


def slave_main():
    # Parse command line arguments:
    # - name: The name of the slave as known to the master controller.
    # - server_port: The TCP port of the command server to bind to.
    # - task_control_module: The name of the module (in sip.slave) to use
    #       for task load and unload functions.
    task_control_module = sys.argv[-1]
    server_port = int(sys.argv[-2])
    name = sys.argv[-3]

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    log.info('Slave controller "{}" starting'.format(name))
    log.info('Slave parameters : {} {}'.format(task_control_module, server_port))
    # Define the module that the task load and unload functions will be
    # loaded from
    _class = getattr(importlib.import_module('sip.slave.task_control'),
                         task_control_module)
    config.task_control = _class()

    # Create and start the RPC server
    from sip.slave.slave_service import SlaveService
    server = ThreadedServer(SlaveService,port=server_port)
    server.start()

if __name__ == '__main__':
    slave_main()
