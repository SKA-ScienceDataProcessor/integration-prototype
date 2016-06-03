"""The master controller states and actions

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 5 events; "online", "offline", "shutdown, "configure done", and 
"unconfigure done".  "online", "offline" and "shutdown are external 
and the others are generated internally.
"""
__author__ = 'David Terrett'

import sys

import logger
from state_machine import StateMachine
from state_machine import State

from .Configure import Configure
from .UnConfigure import UnConfigure

class Standby(State):
    """ Standby state
    """
    def __init__(self):
        super(Standby, self).__init__('standby')
        logger.info('state->standby')

class Configuring(State):
    """ Configuring state
    """
    def __init__(self):
        super(Configuring, self).__init__('configuring')
        logger.info('state->configuring')

class UnConfiguring(State):
    """ Unconfiguring state
    """
    def __init__(self):
        super(UnConfiguring, self).__init__('unconfiguring')
        logger.info('state->unconfiguring')

class Available(State):
    """ Available state
    """
    def __init__(self):
        super(Available, self).__init__('available')
        logger.info('state->available')

def _online(event):
    """Action routine that starts configuring the controller
    """

    # Start a configure thread
    global mc
    Configure(sm).start()

def _offline(event):
    """Action routine that starts un-configuring the controller
    """
    # Start an un-configure thread
    global mc
    UnConfigure(sm).start()

def _shutdown(event):
    """Action routine that shuts down the controller
    """
    sys.exit()

state_table = {
    'standby': {
        'offline':          (0, None, None),
        'online':           (1, Configuring, _online),
        'shutdown':         (1, None, _shutdown)
    },
    'configuring': {
        'configure done' :  (1, Available, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    },
    'available': {
        'offline':          (1, UnConfiguring, _offline),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    },
    'unconfiguring': {
        'unconfigure done': (1, Standby, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    }
}

# Create the master controller state machine
sm = StateMachine(state_table, Standby)
