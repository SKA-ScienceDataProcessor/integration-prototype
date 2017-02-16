# -*- coding: utf-8 -*-
"""Slave controller state machine.

This defines the state machines used to track the state of slave controllers.
"""

from sip_common.logging_api import log
from sip_common.state_machine import State
from sip_common.state_machine import StateMachine
from sip_common.state_machine import _End
from sip_master import config


class Starting(State):
    """Slave starting state."""
    def __init__(self, sm):
        pass


class Idle(State):
    """Slave idle state."""
    def __init__(self, sm):
        log.info('Slave {}  (type {}) idle'.format(sm._name, sm._type))
        pass


class Loading(State):
    """Slave loading state."""
    def __init__(self, sm):
        log.info('{} (type {}) state loading'.format(sm._name, sm._type))


class Busy(State):
    """Slave busy state."""
    def __init__(self, sm):
        log.info('{} (type {}) state online'.format(sm._name, sm._type))


class Finished(State):
    """Slave finished state."""
    def __init__(self, sm):
        log.info('{} (type {}) state finished'.format(sm._name, sm._type))


class Missing(State):
    """Slave missing state."""
    def __init__(self, sm):
        log.info('{} (type {}) state timed-out'.format(sm._name, sm._type))


class Error(State):
    """Slave error state."""
    def __init__(self, sm):
        log.info('{} (type {}) state error'.format(sm._name, sm._type))


class SlaveControllerSM(StateMachine):
    """Slave Controller state machine class."""
    def __init__(self, name, type, task_controller):
        super(SlaveControllerSM, self).__init__(self.state_table, Starting)
        self._name = name
        self._type = type
        self._task_controller = task_controller

    def LoadTask(self, event):
        log.info('Loading slave task. type={}, name={}'.format(self._type,
                                                               self._name))
        self._task_controller.start(self._name,
                                    config.slave_config[self._type],
                                    config.slave_status[self._name])
        self.post_event(['load sent'])

    state_table = {
        'Starting': {
            'idle heartbeat':   (1, Idle, LoadTask),
            'busy heartbeat':   (1, Busy, None),
            'error heartbeat':  (1, Error, None),
            'stop sent':        (1, _End, None)
        },
        'Idle': {
            'busy heartbeat':   (1, Busy, None),
            'load sent':        (1, Loading, None),
            'no heartbeat':     (1, Missing, None),
            'stop sent':        (1, _End, None)
        },
        'Loading': {
            'busy heartbeat':   (1, Busy, None),
            'idle heartbeat':   (1, Idle, None),
            'no heartbeat':     (1, Missing, None),
            'error heartbeat':  (1, Error, None),
            'stop sent':        (1, _End, None)
        },
        'Busy': {
            'idle heartbeat':   (1, Idle, None),
            'no heartbeat':     (1, Missing, None),
            'error heartbeat':  (1, Error, None),
            'stop sent':        (1, _End, None)
        },
        'Missing': {
            'idle heartbeat':   (1, Idle, LoadTask),
            'busy heartbeat':   (1, Busy, None),
            'stop sent':        (1, _End, None)
        },
        'Error': {
            'idle heartbeat':   (1, Idle, LoadTask),
            'busy heartbeat':   (1, Busy, None),
            'stop sent':        (1, _End, None)
        }
}
