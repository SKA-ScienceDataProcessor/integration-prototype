""" Skeleton slave controller 

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

from rpyc.utils.server import ThreadedServer
import threading
import time

from sip_common import heartbeat
from sip_common import logger
from sip_slave import config

def main(name, heartbeat_port, server_port, task_control_module):
    """ Slave controller main program

    Parameters:
        name - The name of the slave as known to the master controller. This
               name is included in the heartbeat messages.
        heatbeat_port - The TCP port to send heatbeat messages to.
        server_port - The TCP port the command server bind to.
        task_control_module - The name of the module (in sip_slave) to load
                              the task load and unload functions from.
    """
    logger.info('Slave controller "' + name + '" starting')

    # Define the modules that the task load and unload functions will be
    # loaded from
    config.task_control_module = task_control_module

    # Now import the slave service.
    from sip_slave.slave_service import SlaveService

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
