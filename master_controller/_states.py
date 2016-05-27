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

from ._configure import _configure
from ._unconfigure import _unconfigure

class standby(State):
    """ Standby state
    """
    def __init__(self):
        self._name = 'standby'
        logger.info('state->standby')

class configuring(State):
    """ Configuring state
    """
    def __init__(self):
        self._name = 'configuring'
        logger.info('state->configuring')

class unconfiguring(State):
    """ Unconfiguring state
    """
    def __init__(self):
        self._name = 'unconfiguring'
        logger.info('state->unconfiguring')

class available(State):
    """ Available state
    """
    def __init__(self):
        self._name = 'available'
        logger.info('state->available')

def _online(event):
    """Action routine that starts configuring the controller
    """

    # Start a configure thread
    global mc
    _configure(sm).start()

def _offline(event):
    """Action routine that starts un-configuring the controller
    """
    # Start an un-configure thread
    global mc
    _unconfigure(sm).start()

def _shutdown(event):
    """Action routine that shuts down the controller
    """
    sys.exit()

state_table = {
    'standby': {
        'offline':          (0, None, None),
        'online':           (1, configuring, _online),
        'shutdown':         (1, None, _shutdown)
    },
    'configuring': {
        'configure done' :  (1, available, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    },
    'available': {
        'offline':          (1, unconfiguring, _offline),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    },
    'unconfiguring': {
        'unconfigure done': (1, standby, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    }
}

# Create the master controller state machine
sm = StateMachine(state_table, standby)
