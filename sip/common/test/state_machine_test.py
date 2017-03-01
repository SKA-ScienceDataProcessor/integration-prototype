import unittest

from sip.common.state_machine import State
from sip.common.state_machine import StateMachine

trace = []


class Offline(State):
    def __init__(self, sm):
        trace.append("entering offline")

    def exit(self):
        trace.append("exiting offline")


class Online(State):
    def __init__(self, sm):
        trace.append("entering online")

    def exit(self):
        trace.append("exiting online")


class TestSM(StateMachine):
    def __init__(self):
        super(TestSM, self).__init__(self.state_table, Offline)

    def action_offline(self, event_name):
        trace.append("going offline")

    def action_online(self, event_name):
        trace.append("going online")

    state_table = {
        'Offline': {
            'start': (1, Online,  action_online),
        },
        'Online' : {
            'stop' : (1, Offline, action_offline),
        }
}


class StateMachineTest(unittest.TestCase):
    def setUp(self):
        self.sm = TestSM()

    def testSimple(self):
        self.sm.post_event(['start'])
        self.assertEqual(self.sm.current_state(), 'Online')
        self.sm.post_event(['start'])
        self.assertEqual(self.sm.current_state(), 'Online')
        self.sm.post_event(['stop'])
        self.assertEqual(self.sm.current_state(), 'Offline')

        self.assertEqual(trace[0], 'entering offline')
        self.assertEqual(trace[1], 'exiting offline')
        self.assertEqual(trace[2], 'going online')
        self.assertEqual(trace[3], 'entering online')
        self.assertEqual(trace[4], 'exiting online')
        self.assertEqual(trace[5], 'going offline')
        self.assertEqual(trace[6], 'entering offline')

if __name__ == "__main__":
    unittest.main()
