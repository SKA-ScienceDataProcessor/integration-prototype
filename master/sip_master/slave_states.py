""" Slave controller state machine

This defines the state machines used to track the state of slave controllers
"""

from sip_common import logger
from sip_common.state_machine import StateMachine
from sip_common.state_machine import State
from sip_common.state_machine import _End
from sip_master import config
from sip_master import task_control

class Starting(State):
    def __init__(self, sm):
        pass

class Idle(State):
    def __init__(self, sm):
        pass

class Loading(State):
    def __init__(self, sm):
        logger.info('{0} state loading'.format(sm._name))

class Busy(State):
    def __init__(self, sm):
        logger.info('{0} state online'.format(sm._name))

class Finished(State):
    def __init__(self, sm):
        logger.info('{0} state finished'.format(sm._name))

class Missing(State):
    def __init__(self, sm):
        logger.info('{0} state timed-out'.format(sm._name))

class SlaveControllerSM(StateMachine):
    def __init__(self, name):
        super(SlaveControllerSM, self).__init__(self.state_table, Starting)
        self._name = name

    def LoadTask(self, event):
        type = config.slave_status[self._name]['type']
        task_control.load(self._name, config.slave_config[type], 
                config.slave_status[self._name]);
        pass

    state_table = {
        'Starting': {
            'idle heartbeat':   (1, Idle, LoadTask),
            'busy heartbeat':   (1, Busy, None)
        },
        'Idle': {
            'busy heartbeat':   (1, Busy, None),
            'load sent':        (1, Loading, None),
            'no heartbeat':     (1, Missing, None)
        },
        'Loading': {
            'busy heartbeat':   (1, Busy, None),
            'idle heartbeat':   (1, Idle, None),
            'no heartbeat':     (1, Missing, None)
        },
        'Busy': {
            'idle heartbeat':   (1, Idle, None),
            'no heartbeat':     (1, Missing, None)
        },
        'Missing': {
            'idle heartbeat':   (1, Idle, LoadTask),
            'busy heartbeat':   (1, Busy, None)
        }
}
