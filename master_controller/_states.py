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
from state_machine import state_machine
from state_machine import state

from ._configure import _configure
from ._unconfigure import _unconfigure

class standby(state):
    """ Standby state
    """
    def __init__(self):
        self._name = 'standby'
        logger.info('state->standby')

class configuring(state):
    """ Configuring state
    """
    def __init__(self):
        self._name = 'configuring'
        logger.info('state->configuring')

class unconfiguring(state):
    """ Unconfiguring state
    """
    def __init__(self):
        self._name = 'unconfiguring'
        logger.info('state->unconfiguring')

class available(state):
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
    _configure(mc).start()

def _offline(event):
    """Action routine that starts un-configuring the controller
    """
    # Start an un-configure thread
    global mc
    _unconfigure(mc).start()

def _shutdown(event):
    """Action routine that shuts down the controller
    """
    sys.exit()

state_table = {
    'standby': {
        'shutdown': (None, _shutdown),
        'online': (configuring, _online)
    },
    'configuring': {
        'configure done': (available, None)
    },
    'available': {
        'offline': (unconfiguring, _offline)
    },
    'unconfiguring': {
        'unconfigure done': (standby, None)
    }
}

# Create the master controller state machine
mc = state_machine(state_table, standby)

 
