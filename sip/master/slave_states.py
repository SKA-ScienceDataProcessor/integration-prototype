# -*- coding: utf-8 -*-
"""Slave controller state machine.

This defines the state machines used to track the state of slave controllers.
"""

import time

from sip.common.logging_api import log
from sip.common.state_machine import State
from sip.common.state_machine import StateMachine
from sip.common.state_machine import _End
from sip.common.paas import TaskStatus
from sip.master import config


class Init(State):
    """Slave init state."""
    def __init__(self, sm):
        pass

class Starting(State):
    """Slave starting state."""
    def __init__(self, sm):
        log.info('{} (type {}) state started'.format(sm._name, sm._type))
        pass


class Running(State):
    """Slave running state."""
    def __init__(self, sm):
        log.info('{} (type {}) state running'.format(sm._name, sm._type))


class Exited(State):
    """Slave exited state."""
    def __init__(self, sm):
        log.info('{} (type {}) state exited'.format(sm._name, sm._type))


class Unknown(State):
    """Slave missing state."""
    def __init__(self, sm):
        log.info('{} (type {}) state unknown'.format(sm._name, sm._type))


class Error(State):
    """Slave error state."""
    def __init__(self, sm):
        log.info('{} (type {}) state error'.format(sm._name, sm._type))


class SlaveControllerSM(StateMachine):
    """Slave Controller state machine class."""
    def __init__(self, name, type, task_controller, init=Init):
        self._name = name
        self._type = type
        self._task_controller = task_controller

        super(SlaveControllerSM, self).__init__(self.state_table, init)

    def LoadTask(self, event):
        log.info('Loading slave task. type={}, name={}'.format(self._type,
                                                               self._name))

        # Connect to the slave controller
        time.sleep(2)
        (host, ports) = config.slave_status[self._name]['descriptor'].location()
        self._task_controller.connect(host, ports[6666])

        # Start the task
        self._task_controller.start(self._name,
                                    config.slave_config[self._type],
                                    config.slave_status[self._name])
    state_table = {
        'Error': {
            TaskStatus.EXITED:   (1, Exited, None),
            TaskStatus.RUNNING : (1, Running, LoadTask),
            TaskStatus.STARTING: (1, Starting, None)
        },
        'Exited': {
            TaskStatus.ERROR:    (1, Error, None),
            TaskStatus.RUNNING : (1, Running, LoadTask),
            TaskStatus.STARTING: (1, Starting, None),
            TaskStatus.UNKNOWN:  (1, Unknown, None)
        },
        'Init': {
            TaskStatus.ERROR:    (1, Error, None),
            TaskStatus.STARTING: (1, Starting, None),
            TaskStatus.RUNNING : (1, Running, LoadTask)
        },
        'Running': {
            TaskStatus.ERROR:     (1, Error, None),
            TaskStatus.EXITED:    (1, Error, None),
            TaskStatus.STARTING:  (1, Error, None), 
            TaskStatus.UNKNOWN:   (1, Unknown, None)
        },
        'Starting': {
            TaskStatus.ERROR:    (1, Error, None),
            TaskStatus.EXITED:   (1, Error, None),
            TaskStatus.RUNNING:  (1, Running, LoadTask),
            TaskStatus.UNKNOWN:  (1, Unknown, None)
        },
        'Unknown': {
            TaskStatus.EXITED:   (1, Exited, None),
            TaskStatus.RUNNING : (1, Running, LoadTask),
            TaskStatus.STARTING: (1, Starting, None)
        }
}
