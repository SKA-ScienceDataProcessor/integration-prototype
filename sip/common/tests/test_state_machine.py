# coding: utf-8
""" Tests of the state machine
"""
import unittest
import time

from sip.common.state_machine import State
from sip.common.state_machine import TimedState
from sip.common.state_machine import StateMachine

TRACE = []  # List of state transitions / actions


class Offline(State):
    """ Offline state
    """
    # pylint: disable=unused-argument
    def __init__(self, state_machine):
        TRACE.append("entering offline")

    def exit(self):
        """ Exit action
        """
        TRACE.append("exiting offline")


class Online(State):
    """ Online state
    """
    # pylint: disable=unused-argument
    def __init__(self, state_machine):
        TRACE.append("entering online")

    def exit(self):
        """ Exit action
        """
        TRACE.append("exiting online")


class Wait(TimedState):
    """ Wait state
    """
    def __init__(self, state_machine):
        TimedState.__init__(self, state_machine, 1, ["timeout"])
        TRACE.append("entering wait")

    def exit(self):
        """ Exit action
        """
        TRACE.append("exiting wait")


class TestSM(StateMachine):
    """ Mock state machine class used for the test.

    Defines a test state machine.
    """
    # pylint: disable=unused-argument, no-self-use

    def __init__(self):
        super(TestSM, self).__init__(self.state_table, Offline)

    def action_offline(self, event_name):
        """ Offline action
        """
        TRACE.append("going offline")

    def action_online(self, event_name):
        """ Online action
        """
        TRACE.append("going online")

    def action_wait(self, event_name):
        """ Wait action
        """
        TRACE.append("waiting")

    state_table = {
        'Offline': {
            'start': (1, Online, action_online),
        },
        'Online': {
            'stop': (1, Offline, action_offline),
            'wait': (1, Wait, action_wait)
        },
        'Wait': {
            'timeout': (1, Offline, action_offline),
        }
    }


class StateMachineTest(unittest.TestCase):
    """ Tests of the State Machine.
    """

    def setUp(self):
        self.state_machine = TestSM()

    def test_simple(self):
        """ Test simple default use of the state machine
        """
        self.state_machine.post_event(['start'])
        self.assertEqual(self.state_machine.current_state(), 'Online')
        self.state_machine.post_event(['start'])
        self.assertEqual(self.state_machine.current_state(), 'Online')
        self.state_machine.post_event(['stop'])
        self.assertEqual(self.state_machine.current_state(), 'Offline')

        self.assertEqual(TRACE[0], 'entering offline')
        self.assertEqual(TRACE[1], 'exiting offline')
        self.assertEqual(TRACE[2], 'going online')
        self.assertEqual(TRACE[3], 'entering online')
        self.assertEqual(TRACE[4], 'exiting online')
        self.assertEqual(TRACE[5], 'going offline')
        self.assertEqual(TRACE[6], 'entering offline')

    def test_timer(self):
        """ Test of timed states (states with a timeout)
        """
        self.state_machine.post_event(['start'])
        self.assertEqual(self.state_machine.current_state(), 'Online')
        self.state_machine.post_event(['wait'])
        self.assertEqual(self.state_machine.current_state(), 'Wait')
        time.sleep(2)
        self.assertEqual(self.state_machine.current_state(), 'Offline')

        self.assertEqual(TRACE[0], 'entering offline')
        self.assertEqual(TRACE[1], 'exiting offline')
        self.assertEqual(TRACE[2], 'going online')
        self.assertEqual(TRACE[3], 'entering online')
        self.assertEqual(TRACE[4], 'exiting online')
        self.assertEqual(TRACE[5], 'going offline')
        self.assertEqual(TRACE[6], 'entering offline')
