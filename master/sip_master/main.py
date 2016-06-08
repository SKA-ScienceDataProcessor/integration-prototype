""" Master controller main program

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 6 events; "online", "offline", "configure done", "unconfigure done"
and "error". "online" and "offline" are external and the others are
generated internally.
"""
__author__ = 'David Terrett + Brian McIlwrath'

import threading

from sip_common.state_machine import StateMachine
from sip_master.states import state_table
from sip_master.states import Standby
from sip_master.heartbeat_listener import HeartbeatListener
from sip_master import config
from sip_master.rpc_service import RpcService

def main():

    # Create the master controller state machine
    config.state_machine = StateMachine(state_table, Standby)

    # Create and start the global heartbeat listener
    config.heartbeat_listener = HeartbeatListener(config.state_machine)
    config.heartbeat_listener.start()

    """ This starts the rpyc 'ThreadedServer' - this creates a new 
        thread for each connection on the given port
    """
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(RpcService,port=12345)
    t = threading.Thread(target=server.start)
    t.setDaemon(True)
    t.start()

    """ For testing we can also run events typed on the terminal
    """
    # Read and process events
    while True:
        event = input('?')
        result = config.state_machine.post_event([event])
        if result == 'rejected':
            print('not allowed in current state')
        if result == 'ignored':
            print('command ignored')
        else:
            print('master controller state:', 
                    config.state_machine.current_state())

