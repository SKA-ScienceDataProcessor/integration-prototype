import unittest

from sip_common.state_machine import State
from sip_common.state_machine import StateMachine

trace = []

class Offline(State):
    def __init__(self):
        super(Offline, self).__init__('offline')
        trace.append("entering offline")
    def exit(self):
        trace.append("exiting offline")
     
class Online(State):
    def __init__(self):
        super(Online, self).__init__('online')
        trace.append("entering online")
    def exit(self):
        trace.append("exiting online")

def action_offline(event_name):
    trace.append("going offline")

def action_online(event_name):
    trace.append("going online")

state_table = {
    'offline': {
        'start': (1, Online,  action_online),
    },
    'online' : {
        'stop' : (1, Offline, action_offline),
    }
}

class StateMachineTest(unittest.TestCase):
    def setUp(self):
        self.sm = StateMachine(state_table, Offline)

    def testSimple(self):
        self.sm.post_event(['start'])
        self.assertEqual(self.sm.current_state(), 'online')
        self.sm.post_event(['start'])
        self.assertEqual(self.sm.current_state(), 'online')
        self.sm.post_event(['stop'])
        self.assertEqual(self.sm.current_state(), 'offline')

        self.assertEqual(trace[0], 'entering offline')
        self.assertEqual(trace[1], 'exiting offline')
        self.assertEqual(trace[2], 'going online')
        self.assertEqual(trace[3], 'entering online')
        self.assertEqual(trace[4], 'exiting online')
        self.assertEqual(trace[5], 'going offline')
        self.assertEqual(trace[6], 'entering offline')

if __name__ == "__main__":
    unittest.main()
