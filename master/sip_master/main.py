# -*- coding: utf-8 -*-
"""Master controller main program.

1. Creates a Resource Manager object.
   :class:`sip_common.resource_manager.ResourceManager`..
2. Starts the logger (log aggregator) as a subprocess.
3. Loads the slave configuration JSON file (``slave_map.json``).
4. Creates the Master Controller state machine:
   :class:`sip_master.master_states.MasterControllerSM`.
5. Creates the Master Controller RPC interface.
   :class:`sip_master.rpc_service.RpcService`.
6. Enters a event loop waiting for command line inputs.

The master controller implements a simple state machine (see
`state machine uml`_).

.. _state machine uml: https://goo.gl/Xyri5Q
"""
import json
import threading
import subprocess
import os
import time

from sip_common.resource_manager import ResourceManager
from sip_common import logger as log
from sip_master.master_states import MasterControllerSM
from sip_master.master_states import Standby
from sip_master.heartbeat_listener import HeartbeatListener
from sip_master import config
from sip_master.rpc_service import RpcService

__author__ = 'David Terrett + Brian McIlwrath'


def main(config_file, resources_file):
    """Master controller main program.

    Args:
        config_file (str): JSON slave configuration file.
        resources_file (str): JSON resources file.
    """

    # Create the resource manager
    with open(resources_file) as f:
        _resources = json.load(f)
        # If using localhost, and sip root is set to #cwd replace it.
        if 'localhost' in _resources and \
                _resources['localhost']['sip_root'] == '#cwd':
            _resources['localhost']['sip_root'] = os.getcwd()
        print('Resource table:')
        for i, resource in enumerate(_resources):
            print('[{:03d}] {}'.format(i, resource))
            for key, value in _resources[resource].items():
                print('  - {} {}'.format(key, value))
        config.resource = ResourceManager(_resources)

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
