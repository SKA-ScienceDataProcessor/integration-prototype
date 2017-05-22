# -*- coding: utf-8 -*-
"""Slave controller state machine.

This defines the state machines used to track the state of slave controllers.
"""

import copy
from enum import Enum
import time

from sip.common.logging_api import log
from sip.common.state_machine import State
from sip.common.state_machine import StateMachine
from sip.common.state_machine import _End
from sip.common.paas import TaskStatus, TaskDescriptor
from sip.master.config import slave_status
from sip.master.config import slave_config

import sip.master.task_control as tc

class SlaveStatus(Enum):
    noConnection = 0
    idle = 1
    busy = 2
    error = 3


class Init(State):
    """Slave init state."""
    def __init__(self, sm):
        pass

class Starting(State):
    """Slave starting state."""
    def __init__(self, sm):
        log.info('{} (type {}) state started'.format(sm._name, sm._type))
        pass


class Running_noConnection(State):
    """Slave running state put no rpyc connection."""
    def __init__(self, sm):
        log.info('{} (type {}) state running_noConnection'.format(sm._name, 
                sm._type))
        sm.Connect()


class Running_idle(State):
    """Slave running in state idle state."""
    def __init__(self, sm):
        log.info('{} (type {}) state running_idle'.format(sm._name, 
                sm._type))

        # If the restart flag is set, command the slave to restart the task.
        if slave_status(sm._name)['restart']:
            sm.LoadTask()

            # If this isn't an "online" task turn off restart
            if not slave_config(sm._name)['online']:
                slave_status(sm._name)['restart'] = False


class Running_busy(State):
    """Slave running in state busy state."""
    def __init__(self, sm):
        log.info('{} (type {}) state running_busy'.format(sm._name, 
                sm._type))


class Running_error(State):
    """Slave running in state error state."""
    def __init__(self, sm):
        log.info('{} (type {}) state running_error'.format(sm._name, 
                sm._type))


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
    def __init__(self, name, type, task_controller, init=Init, descriptor=None):
        self._name = name
        self._type = type
        self._task_controller = task_controller

        if descriptor:
            self._descriptor = descriptor
        else:
            self._descriptor = None

        super(SlaveControllerSM, self).__init__(self.state_table, init)

    def Connect(self, event=None):
        log.info('Attempting to connect to slave task. type={}, name={}'. \
                format(self._type, self._name))
        try:
            if isinstance(self._task_controller, tc.SlaveTaskControllerRPyC):
                (host, port) = \
                    slave_status(self._name)['descriptor'].location(6666)
                self._task_controller.connect(host, port)
            elif isinstance(self._task_controller, tc.SlaveTaskControllerSpark):
                if isinstance(event, TaskDescriptor):
                    self._descriptor = event
                self._task_controller.connect(self._descriptor)
        except:
            pass

    def LoadTask(self, event=None):
        log.info('Loading slave task. type={}, name={}'.format(self._type,
                                                               self._name))

        # Start the task
        self._task_controller.start(self._name, slave_config(self._name),
                                    slave_status(self._name))


    # Define a default table which just moves the state machine to the
    # state corresponding to the event with no action routines
    default = {
        TaskStatus.EXITED:    (1, Exited, None),
        TaskStatus.ERROR:    (1, Error, None),
        TaskStatus.STARTING: (1, Starting, None),
        TaskStatus.UNKNOWN:  (1, Unknown, None),
        SlaveStatus.noConnection : (1, Running_noConnection, None),
        SlaveStatus.idle : (1, Running_idle, None),
        SlaveStatus.busy : (1, Running_busy, None),
        SlaveStatus.error : (1, Running_error, None)
    }

    # Construct the state table using copies of the default
    state_table = {}
    state_table['Error'] = copy.copy(default)
    state_table['Exited'] = copy.copy(default)
    state_table['Init'] = copy.copy(default)
    state_table['Starting'] = copy.copy(default)
    state_table['Unknown'] = copy.copy(default)
    state_table['Running_noConnection'] = copy.copy(default)
    state_table['Running_idle'] = copy.copy(default)
    state_table['Running_busy'] = copy.copy(default)
    state_table['Running_error'] = copy.copy(default)

    # Remove the entries that result in a transition to the same state except
    # for the no connection state where we want to keep trying if the
    # connection attempt fails
    del state_table['Error'][TaskStatus.ERROR]
    del state_table['Exited'][TaskStatus.EXITED]
    del state_table['Starting'][TaskStatus.STARTING]
    del state_table['Unknown'][TaskStatus.UNKNOWN]
    del state_table['Running_idle'][SlaveStatus.idle]
    del state_table['Running_busy'][SlaveStatus.busy]
    del state_table['Running_error'][SlaveStatus.error]

    # Update the entries where we want some action.
