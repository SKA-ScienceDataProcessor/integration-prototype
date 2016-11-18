from collections import deque
import threading

""" State machine framework

This module defines a simple state machine framework. It supports entry,
exit and transition actions and in-state transitions. It does not support
nested states or a history states.

States are represented by objects derived from "State" and their __init__ 
and exit methods (if they exist) define the state entry and exit actions. 
The __init__ method must have one parameter which is a reference to the
state machine.

The state machine is a class that inherits "StateMachine" and transition 
actions are state machine methods.

The state diagram is stored in a dictionary with an entry per state. The 
value of each entry is a dictionary with the key being events and the value 
a tuple containing whether the event should be accepted (1) or rejected
(0), destination state and the name of the transition 
action method. If an event is not in the table it is ignored.

Events are represented by arrays or tuples (or anything that supports [] with
numeric arguments) the first element of which is used to look up entries in
the state table. The remaining elements are passed to the action function
as positional arguments.

The method for posting events to the state machine returns a string 
indicating whether the event was accepted ('ok'), rejected or ignored.

The get_graph method creates a pygraphvis representation of the state machine.
"""

# pygraphviz is only needed for the method that creates a graphviz 
# representation of the state machine. This in not needed to use the state
# machine so, if we can't import it we ignore the error.
try:
    import pygraphviz as pgv
except:
    pass


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

    This state is used as the destination of any transition that ends the
    state machine. It has a special name so that the graph represention can
    use the correct symbol.
    """
    def __init__(self, sm):
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

        # Add an entry for the end state
        state_table['_End'] = {}

        # Set the initial state
        self._state = initial_state(self)

        # Create empty event queue
        self._event_queue = deque()

        # Prime the coroutine
        self._state_machine = self._run()
        next(self._state_machine)

        # Create a lock object for ensuring that posting events is single
        # threaded.
        self._lock = threading.Lock()

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
                action(self, event[0], *event[1:])

            # If there is a new state, create it.
            if new_state:
                self._state = new_state(self)
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
            event = yield result
    
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

        If called recursively (i.e. from an action routine) the event is
        just placed on the back of the event queue.
        """
        if self._lock.acquire(blocking=False):
            result = self._state_machine.send(event)
            self._lock.release()
            return result
        else:
            self.queue_event(event)

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

    def get_graph(self, title=''):
        """ Return graphviz representation of the state machine

            The state machine's current state is taken to the the initial
            state so this method should be called before the state machine
            has been run.
        """

        # Create a graph
        graph = pgv.AGraph(title=title, directed=True, strict=False,
                           rankdir='LR', ratio='0.3')

        # Create a node for each state
        for state in self._state_table:
            graph.add_node(n=state, shape='box', height='1.2')

        # Create a start node
        graph.add_node('start', shape='circle', height='0.1')
        graph.add_edge('start', type(self._state).__name__)

        # Create an end node
        graph.add_node('_End', shape='circle', height='0.1', label='end')

        # Add an edge for every transition.
        for state, events in self._state_table.items():
            for event, transition in events.items():
                if transition[0] == 1:

                    # For in-state transitions the destination is the
                    # current state
                    destination = transition[1]
                    if destination is None:
                        destination = state
                    else:
                        destination = destination.__name__

                    # Label the edge with the event name
                    label = event

                    # Add the name of the action if there is one
                    if transition[2]:
                        label += '/' + transition[2].__name__
                    graph.add_edge(state, destination, label=label)
        return graph
