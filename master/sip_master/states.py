"""The master controller states and actions

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 5 events; "online", "offline", "shutdown, "configure done", and 
"unconfigure done".  "online", "offline" and "shutdown are external 
and the others are generated internally.
"""
__author__ = 'David Terrett'

import sys

from sip_common import logger
from sip_common.state_machine import StateMachine
from sip_common.state_machine import State

from sip_master.configure import Configure
from sip_master.un_configure import UnConfigure
from sip_master.shutdown import Shutdown

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

class Degraded(State):
    """ Degraded state
    """
    def __init__(self):
        super(Degraded, self).__init__('degraded')
        logger.info('state->degraded')

class Unavailable(State):
    """ Unavailable state
    """
    def __init__(self):
        super(Unavailable, self).__init__('unavailable')
        logger.info('state->unavailable')

def _online(event):
    """Action routine that starts configuring the controller
    """

    # Start a configure thread
    Configure().start()

def _offline(event):
    """Action routine that starts un-configuring the controller
    """
    # Start an un-configure thread
    UnConfigure().start()

def _shutdown(event):
    """Action routine that shuts down the controller
    """
    # Start an un-configure thread
    Shutdown().start()

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
        'shutdown':         (0, None, None),
        'degrade':          (1, Degraded, None)
    },
    'degraded': {
        'offline':          (1, UnConfiguring, _offline),
        'online':           (0, None, None),
        'shutdown':         (0, None, None),
        'upgrade':          (1, Available, None),
        'degrade':          (1, Unavailable, None)
    },
    'unavailable': {
        'offline':          (1, UnConfiguring, _offline),
        'online':           (0, None, None),
        'shutdown':         (0, None, None),
        'upgrade':          (1, Degraded, None)
    },
    'unconfiguring': {
        'unconfigure done': (1, Standby, None),
        'offline':          (0, None, None),
        'online':           (0, None, None),
        'shutdown':         (0, None, None)
    }
}
