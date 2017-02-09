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

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from sip.slave import config


def _sig_handler(signum, frame):
    sys.exit(0)


def slave_main():
    # Parse command line arguments:
    # - name: The name of the slave as known to the master controller.
    # - heartbeat_port: The TCP port to send heartbeat messages to.
    # - server_port: The TCP port of the command server to bind to.
    # - logging_address: Address of the log server.
    # - task_control_module: The name of the module (in sip.slave) to use
    #       for task load and unload functions.
    task_control_module = sys.argv[-1]
    logging_address = sys.argv[-2]
    server_port = int(sys.argv[-3])
    heartbeat_port = int(sys.argv[-4])
    name = sys.argv[-5]

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # Define SIP_HOSTNAME
    os.environ['SIP_HOSTNAME'] = logging_address
    from sip.common.logging_api import log
    log.info('Slave controller "{}" starting'.format(name))

    # Define the module that the task load and unload functions will be
    # loaded from
    config.task_control_module = task_control_module

    # Create a heartbeat sender to MC
    from sip.common import heartbeat
    heartbeat_sender = heartbeat.Sender(name, heartbeat_port)

    # Create and start the RPC server
    from sip.slave.slave_service import SlaveService
    server = ThreadedServer(SlaveService,port=server_port)
    t = threading.Thread(target=server.start)
    t.setDaemon(True)
    t.start()

    # Send heartbeats
    while True:
        heartbeat_sender.send(config.state)
        time.sleep(1)

if __name__ == '__main__':
    slave_main()
