""" State machine framework

This module defines a simple state machine framework. It supports entry,
exit and transition actions and in-state transitions. It does not support
nested states or a history states.

States are represented by objects derived from "State" and their __init__ 
and __del__ methods (if the exist) define the state entry and exit actions. 
The state diagram is stored in a dictionary with an entry per state. The 
value of each entry is a dictionary with the key being events and the value 
a tuple containing whether the event should be accepted (1) or rejected
(0), destination state and the name of the transition 
action function. If an event is not in the table it is ignored.

Events are represented by arrays or tuples (or anything that supports [] with
numeric arguments) the first element of which is used to look up entries in
the state table. The remaining elements are passed to the action function
as positional arguments.

post_event returns a string indicating whether the event was accepted ('ok'),
rejected or ignored.
"""
__author__ = 'David Terrett'

from collections import deque

class State:
    """ Base class for states

    The derived class must set self._name to the name of the state
    """
    def process_event(self, state_table, event):

         # Check that the event is in the table
         if event[0] in state_table[self._name]:

             # Return the table entry for this event
             transition = state_table[self._name][event[0]]
             return transition

         # No transition defined for this event
         return (None, None, None)

class StateMachine:
    """ State machine
    """
    def __init__(self, state_table, initial_state):
        """ Constructor
    
        Stores the state table, creates the initial state and calls _run
        to initialise the coroutine.
        """
        self._state_table = state_table
        self._state = initial_state()

        # Create empty event queue
        self._event_queue = deque()

        # Prime the coroutine
        self._state_machine = self._run()
        next(self._state_machine)

    def _process_one_event(self, event):
        """ Process a single event
        """

        # Get the new state and transition action from the state table
        status, new_state, action = self._state.process_event(
                self._state_table, event)

        if status == 1:
            # If there is a new state, destroy the current state
            if new_state:
                self._state = None

            # If there is an action, call it.
            if action:
                action(event[0], *event[1:])

            # If there is a new state, create it.
            if new_state:
                self._state = new_state()
            return 'ok'
        elif status == 0:
            return 'rejected'
        return 'ignored'

    def _run(self):
        """ State machine event loop
    
        This a coroutine that loops for ever. When the event queue is empty 
        it yields control until 'send' is called
        """
        result = None
        while True:
            event = yield(result)
    
            # If there are any events in the queue, process them.
            while len(self._event_queue) > 0:
                self._process_one_event(self._event_queue.pop())

            # Process the event we were just sent and save the result
            result = self._process_one_event(event)
    
            # If process any events added to the queue
            while len(self._event_queue) > 0:
                self._process_one_event(self._event_queue.pop())

    def post_event(self, event):
        """ Post an event to the state machine

        This causes the state machine to process the event queue and must not
        be called from a state machine action routine. queue_event should 
        be used instead.
        """
        return self._state_machine.send(event)

    def queue_event(self, event):
        """ Add an event to the event queue
    
        This adds an event to the queue but does not cause the queue to be
        processed. It can be called from a state machine action routine and
        the event will be processed when control has returned to the state
        machine _run method.
        """
        self._event_queue.appendleft(event)

if __name__ == "__main__":

    import sys

    # Simple demo state machine

    class offline(State):
        def __init__(self):
            self._name = 'offline'
            print("entering offline")
        def __del__(self):
            print("exiting offline")
         
    class online(State):
        def __init__(self):
            self._name = 'online'
            print("entering online")
        def __del__(self):
            print("exiting online")

    def action_offline(event_name):
        print("going off-line")

    def action_online(event_name):
        print("going on-line")

    def action_exit(event_name):
        print("Bye...")
        sys.exit()

    state_table = {
        'offline': {
            'start': (1, online,  action_online),
            'exit':  (1, None,    action_exit)
        },
        'online' : {
            'stop' : (1, offline, action_offline),
            'exit':  (0, None, None)
        }
    }

    sm = StateMachine(state_table, offline)

    print('start', sm.post_event(['start']))
    print('start', sm.post_event(['start']))
    print('exit', sm.post_event(['exit']))
    print('stop', sm.post_event(['stop']))
    print('exit', sm.post_event(['exit']))
