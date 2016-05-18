from collections import deque
import sys
import threading
import time

import logger

"""The integration prototype master controller

The master controller implements a simple state machine. It only
has 4 states; "standby", "configuring", "available" and "unconfiguring"
and 6 events; "online", "offline", "configure done", "unconfigure done"
and "error". "online" and "offline" are external and the others are
generated internally.

This needs to be replaced by a proper grown-up FSM.
"""

# The state machine's current state
_state = 'standby'

# The queue of events waiting to be processed
_event_queue = deque()


def start():
    """ Start the master controller state machine
    """

    # The state machine event handler is implemented as a coroutine which
    # must be stored and then executed to start it.
    global _state_machine
    _state_machine = run()
    next(_state_machine)
    logger.info('Master controller started')

def run():
    """ State machine event loop
    
    This a coroutine that loops until the state become 'exit'. When the
    event queue is empty it relinquishes control until 'send' is called
    """
    global _event_queue

    # Loop until the state is 'exit' (which isn't really a state)
    while  _state != 'exit':
        event = yield
        _event_queue.appendleft(event)

        # If there are any events in the queue, process them.
        while len(_event_queue) > 0:
            _process_event(_event_queue.pop())
    sys.exit()

def _process_event(event):
    """Process an event

    This function does the work of processing a single event; calling the
    appropriate action routine and setting the new state as returned by
    the action routine.
    """
    global _state
    logger.trace('processing event "' + event + '"')
    new_state = _state
    if _state == 'standby':
        if event == 'online':
            new_state = _action_online()
        elif event == 'shutdown':
            new_state = _action_shutdown()
        else:
            logger.warn('event ignored')
    elif _state == 'configuring':
        if event == 'configure done':
            new_state = 'available'
        else:
            logger.warn('event ignored')
    elif _state == 'un-configuring':
        if event == 'un-configure done':
            new_state = 'standby'
        else:
            logger.warn('event ignored')
    elif _state == 'available':
        if event == 'offline':
            new_state = _action_offline()
        else:
            logger.warn('event ignored')

    # Change to new state
    if new_state != _state:
        logger.trace('state-> ' + new_state)
        _state = new_state

def post_event(event):
    """ Post an event to the state machine

    This causes the state machine to process the event queue and must not
    be called from a state machine action routine. queue_event should be used 
    instead.
    """
    _state_machine.send(event)

def queue_event(event):
    """ Add an event to the event queue

    This adds an event to the queue but does not cause the queue to be
    processed. It can be called from a state machine action routine.
    """
    global _event_queue
    _event_queue.appendleft(event)

def _action_online():
    """Action routine that starts configuring the controller
    """

    # Do stuff in the background
    _configure().start()
    
    return 'configuring'

def _action_offline():
    """Action routine that starts un-configuring the controller
    """
    # Do stuff in the background
    _unconfigure().start()
    
    return 'un-configuring'

def _action_shutdown():
    """Action routine that shuts down the controller
    """
    return 'exit'

class _configure(threading.Thread):
    """ Does the actual work of configuring the system

    All it does for now is sleep for 10 seconds
    """
    def run(self):
        logger.trace('starting configuration')
        time.sleep(10)
        logger.trace('configure done')
        post_event('configure done')


class _unconfigure(threading.Thread):
    """ Does the actual work of un-configuring the system

    All it does for now is sleep for 5 seconds
    """
    def run(self):
        logger.trace('starting un-configuration')
        time.sleep(5)
        logger.trace('un-configure done')
        post_event('un-configure done')

if __name__ == "__main__":
    """ For testing we simply post events typed on the terminal
    """

    # Create the master controller
    start()

    # Read and process events
    while True:
        event = input('?')
        post_event(event)

