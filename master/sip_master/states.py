"""The master controller states and actions

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 5 events; "online", "offline", "shutdown, "cap", "configure done", and 
"unconfigure done".  "cap", "online", "offline" and "shutdown are external 
and the others are generated internally.
"""
__author__ = 'David Terrett'

import sys

from sip_common import logger
from sip_common.state_machine import StateMachine
from sip_common.state_machine import State
from sip_common.state_machine import _End

from sip_master.capability import Capability
from sip_master.configure import Configure
from sip_master.un_configure import UnConfigure
from sip_master.shutdown import Shutdown

class Standby(State):
    """ Standby state
    """
    def __init__(self):
        logger.info('state->standby')

class Configuring(State):
    """ Configuring state
    """
    def __init__(self):
        logger.info('state->configuring')

class UnConfiguring(State):
    """ Unconfiguring state
    """
    def __init__(self):
        logger.info('state->unconfiguring')

class Available(State):
    """ Available state
    """
    def __init__(self):
        logger.info('state->available')

class Degraded(State):
    """ Degraded state
    """
    def __init__(self):
        logger.info('state->degraded')

class Unavailable(State):
    """ Unavailable state
    """
    def __init__(self):
        logger.info('state->unavailable')

def _online(event):
    """Action routine that starts configuring the controller
    """

    # Start a configure thread
    Configure().start()

def _cap(event, *args):
    """ Action routine that starts a capability
    """
    Capability(*args).start()

def _offline(event):
    """Action routine that starts un-configuring the controller
    """
    # Start an un-configure thread
    UnConfigure().start()

def _shutdown(event):
    """Action routine that shuts down the controller
    """
    # Start an shutdown thread
    Shutdown().start()

state_table = {
    'Standby': {
        'offline':          (0, None, None),
        'online':           (1, Configuring, _online),
        'shutdown':         (1, _End, _shutdown)
    },
    'Configuring': {
        'configure done' :  (1, Available, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    },
    'Available': {
        'offline':          (1, UnConfiguring, _offline),
        'online':           (0, None, None),
        'cap':              (1, None, _cap),
        'shutdown':         (0, None, None),
        'degrade':          (1, Degraded, None)
    },
    'Degraded': {
        'offline':          (1, UnConfiguring, _offline),
        'online':           (0, None, None),
        'shutdown':         (0, None, None),
        'upgrade':          (1, Available, None),
        'degrade':          (1, Unavailable, None)
    },
    'Unavailable': {
        'offline':          (1, UnConfiguring, _offline),
        'online':           (0, None, None),
        'shutdown':         (0, None, None),
        'upgrade':          (1, Degraded, None)
    },
    'UnConfiguring': {
        'unconfigure done': (1, Standby, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    }
}
