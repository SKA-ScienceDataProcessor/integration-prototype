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

import sys
import json
import threading
import subprocess
import os
import time
import logging.handlers
from rpyc.utils.server import ThreadedServer

# Export environment variable SIP_HOSTNAME
# This is needed before the other SIP imports.
os.environ['SIP_HOSTNAME'] = os.uname()[1]

from sip.common.resource_manager import ResourceManager
from sip.common.docker_paas import DockerPaas as Paas
from sip.master import config

__author__ = 'David Terrett + Brian McIlwrath'

sip_root = os.path.join(os.path.dirname(__file__), '..')
config_file = os.path.join(sip_root, 'etc', 'slave_map.json')
resources_file = os.path.join(sip_root, 'etc', 'resources.json')

# Create the resource manager
with open(resources_file) as f:
    _resources = json.load(f)
    # If using localhost, and sip root is set to #cwd replace it.
    # if 'localhost' in _resources and \
    #                 _resources['localhost']['sip_root'] == '#cwd':
    #     _resources['localhost']['sip_root'] = os.getcwd()
    # FIXME(FD) Check this is an acceptable change.
    if 'localhost' in _resources:
        _resources['localhost']['sip_root'] = sip_root
    print('Resource table:')
    for i, resource in enumerate(_resources):
        print('[{:03d}] {}'.format(i, resource))
        for key, value in _resources[resource].items():
            print('  - {} {}'.format(key, value))
    config.resource = ResourceManager(_resources)

# "Allocate" localhost for the master controller so that we can
# allocate it resources.
    config.resource.allocate_host(
            "Master Controller", {'host': 'localhost'}, {})

# Start logging server
    paas = Paas()
    config.logserver = paas.run_service('logging_server', 'sip',
        [logging.handlers.DEFAULT_TCP_LOGGING_PORT],
        ['python3', 'sip/common/logging_server.py'])

    from sip.common.logging_api import log
    from sip.master.master_states import MasterControllerSM
    from sip.master.master_states import Standby
    from sip.master.heartbeat_listener import HeartbeatListener
    from sip.master.rpc_service import RpcService

# Wait until it initializes
time.sleep(1.0)

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
server = ThreadedServer(RpcService, port=12345)
t = threading.Thread(target=server.start)
t.setDaemon(True)
t.start()

# For testing we can also post events typed on the terminal
while True:
    # Read from the terminal and process the event
    event = input('** Enter command:\n').split()
    if event:
        if event[0] == 'state':
            log.info('CLI: Current state: {}'.
                     format(config.state_machine.current_state()))
            continue
        log.info('CLI: !!! Posting event ==> {}'.format(event[0]))
        result = config.state_machine.post_event(event)
        if result == 'rejected':
            log.warn('CLI: not allowed in current state')
        elif result == 'ignored':
            log.warn('CLI: command ignored: {}'.format(event[0]))
        else:
            # Print what state we are now in.
            log.info('CLI: master controller state: {}'.format(
                config.state_machine.current_state()))
    # else:
    #     print('** Allowed commands: online, offline, shutdown, '
    #           'cap [name] [task]')
