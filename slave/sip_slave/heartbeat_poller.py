""" Class for polling for heartbeat messages from a task
"""
import time
import threading

from sip_common import heartbeat
from sip_common import heartbeat_task
from sip_common import logger
from sip_slave import config

def _get_state(msg):
    """ extracts the state from the heartbeat message
    """
    tokens = msg.split(" ")
    if len(tokens) < 4 :
         tokens = [' ', ' ', ' ', 'off', ' ', ' ']
    return tokens[3]	

class HeartbeatPoller(threading.Thread):
    """ Polls for heartbeat messages from the task
    """
    def __init__(self, heartbeat_comp_listener):
        self._state_task_prev = ''
        self._heartbeat_comp_listener = heartbeat_comp_listener
        super(HeartbeatPoller, self).__init__(daemon=True)
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
