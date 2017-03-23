#!/usr/bin/python3
"""Skeleton slave controller.

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

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
    # - logging_address: Address of the log server.
    # - task_control_module: The name of the module (in sip.slave) to use
    #       for task load and unload functions.
    task_control_module = sys.argv[-1]
    logging_address = sys.argv[-2]
    server_port = int(sys.argv[-3])
    name = sys.argv[-4]

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    log.info('Slave controller "{}" starting'.format(name))

    # Define the module that the task load and unload functions will be
    # loaded from
    config.task_control_module = task_control_module

    # Create and start the RPC server
    from sip.slave.slave_service import SlaveService
    server = ThreadedServer(SlaveService,port=server_port)
    t = threading.Thread(target=server.start)
    t.setDaemon(True)
    t.start()

    # Wait forever
    while True:
        time.sleep(1)

if __name__ == '__main__':
    slave_main()
