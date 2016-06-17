""" State machine framework

This module defines a simple state machine framework. It supports entry,
exit and transition actions and in-state transitions. It does not support
nested states or a history states.

States are represented by objects derived from "State" and their __init__ 
and exit methods (if they exist) define the state entry and exit actions. 
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

from collections import deque

class State:
    """ Base class for states
    """
    def process_event(self, state_table, event):
        """ Processes an event
            
        The event is looked up in the state table and if an entry exists
        it is return. Otherwise a tuple of None's is returned.
        """

        # Check that the event is in the table
        if event[0] in state_table[type(self).__name__]:

            # Return the table entry for this event
            transition = state_table[type(self).__name__][event[0]]
            return transition

        # No transition defined for this event
        return (None, None, None)

    def exit(self):
        """ Default exit action
        """
        pass

class _End(State):
    """ Pseudo end state
    """
    def __init__(self):
        pass

class StateMachine:
    """ State machine
    """
    def __init__(self, state_table, initial_state):
        """ Creates and initialise a state machine
    
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
                self._state.exit()
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

    def current_state(self):
        """ Returns the name of the current state
        """
        return type(self._state).__name__
