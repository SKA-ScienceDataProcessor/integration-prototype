""" Skeleton slave controller for use in a Docker container

All it does is send heartbeat messages to MC.

It also can start a component, currently /home/sdp/components/component.py,
monitor it's hearbeat messages, extract the component's state and write 
into a system log when the state changes.

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

from rpyc.utils.server import ThreadedServer
import threading
import time

from sip_common import heartbeat
from sip_common import logger
from sip_slave.slave_service import SlaveService
from sip_slave.load import load
from sip_slave import config

def main(name, heartbeat_port, server_port):
    logger.info('Slave controller "' + name + '" starting')

    # Create a heartbeat sender to MC
    heartbeat_sender = heartbeat.Sender(name, heartbeat_port)

    # Create and start the RPC server
    server = ThreadedServer(SlaveService,port=server_port)  
    t = threading.Thread(target=server.start)
    t.setDaemon(True)
    t.start()

    # Send heartbeats
    while True:
        heartbeat_sender.send(config.state)
        time.sleep(1)
