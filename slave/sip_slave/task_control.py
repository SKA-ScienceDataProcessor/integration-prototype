""" This module defines the load and unload functions for controlling an
'internal' SIP task.

An internal task sends heartbeat messages to its controller.
"""

import subprocess
import time
import threading

from sip_common import heartbeat
from sip_common import heartbeat_task
from sip_common import logger
from sip_slave import config

def load(task):
    """ load the task

    Some sort of task monitoring process should also be started. For
    'internal' tasks this means checking that the task has is sending
    heartbeat messages
    """
    _state_task = 'off'
    _state_task_prev = 'off'

    # Extract the port number
    port = int(task[1])

    # Start a task
    logger.info('Starting task {}'.format(task[0]))
    config.subproc = subprocess.Popen(task)

    # Create a heartbeat listener to listen for a task
    timeout_msec = 1000
    heartbeat_comp_listener = heartbeat_task.Listener(timeout_msec)
    heartbeat_comp_listener.connect('localhost', port)
    config.poller = _HeartbeatPoller(heartbeat_comp_listener)
    config.poller_run = True
    config.poller.start()

def unload(task):
    """ Unload the task
    """
    logger.info('unloading task {}'.format(task[0]))

    # Stop the heartbeat poller
    config.poller_run = False

    # Kill the sub-process
    config.subproc.kill()

    # Reset state
    config.state = 'idle'

def _get_state(msg):
    """ extracts the state from the heartbeat message
    """
    tokens = msg.split(" ")
    if len(tokens) < 4 :
         tokens = [' ', ' ', ' ', 'off', ' ', ' ']
    return tokens[3]	

class _HeartbeatPoller(threading.Thread):
    """ Polls for heartbeat messages from the task
    """
    def __init__(self, heartbeat_comp_listener):
        self._state_task_prev = ''
        self._heartbeat_comp_listener = heartbeat_comp_listener
        super(_HeartbeatPoller, self).__init__(daemon=True)
    def run(self):
        while config.poller_run:

            # Listen to the task's heartbeat
            comp_msg = self._heartbeat_comp_listener.listen()

	    # Extract a task's state
            state_task = _get_state(comp_msg)

	    # If the task state changes log it
            if state_task != self._state_task_prev :
                 logger.info(comp_msg)
                 self._state_task_prev = state_task		

            # Update the controller state
            if state_task == 'starting' or state_task == 'state1' or \
                    state_task == 'state2':
                config.state = 'busy'
            else:
                config.state = state_task
            time.sleep(1)
