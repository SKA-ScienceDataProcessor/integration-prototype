""" Master controller main program

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 6 events; "online", "offline", "configure done", "unconfigure done"
and "error". "online" and "offline" are external and the others are
generated internally.
"""
__author__ = 'David Terrett + Brian McIlwrath'

import json
import threading
import subprocess
import os
import time

from sip_common.resource_manager import ResourceManager
from sip_master.master_states import MasterControllerSM
from sip_master.master_states import Standby
from sip_master.heartbeat_listener import HeartbeatListener
from sip_master import config
from sip_master.rpc_service import RpcService

def main(config_file, resources_file):

    # Create the resource manager
    with open(resources_file) as f:
        config.resource = ResourceManager(json.load(f))

    # "Allocate" localhost for the master controller so that we can
    # allocate it resources.
    config.resource.allocate_host("Master Controller",
            {'host': 'localhost'}, {})

    # Start logging server as a subprocess
    config.logserver = subprocess.Popen(
            'common/sip_common/logging_server.py', shell=False)

    # Wait until it initializes
    time.sleep(2)

    # Create the slave config array from the configuration (a JSON string)
    with open(config_file) as f:
        config.slave_config = json.load(f)

    # Create the master controller state machine
    config.state_machine = MasterControllerSM()

    # Create and start the global heartbeat listener
    config.heartbeat_listener = HeartbeatListener(config.state_machine)
    config.heartbeat_listener.start()

    # This starts the rpyc 'ThreadedServer' - this creates a new
    # thread for each connection on the given port
    from rpyc.utils.server import ThreadedServer
    server = ThreadedServer(RpcService,port=12345)
    t = threading.Thread(target=server.start)
    t.setDaemon(True)
    t.start()

    # For testing we can also post events typed on the terminal
    while True:

        # Read from the terminal and process the event
        event = input('?').split()
        if event:
            if event[0] == 'state':
                print('Current state: ', config.state_machine.current_state())
                continue
            result = config.state_machine.post_event(event)
            if result == 'rejected':
                print('not allowed in current state')
            if result == 'ignored':
                print('command ignored')
            else:

                # Print what our state we are now in.
                print('master controller state:',
                        config.state_machine.current_state())
