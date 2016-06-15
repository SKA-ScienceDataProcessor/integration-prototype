""" Class for polling for heartbeat messages from a component
"""
import time
import threading

from sip_common import heartbeat
from sip_common import heartbeat_component
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
    """ Polls for heartbeat messages from the component
    """
    def __init__(self, heartbeat_comp_listener):
        self._state_component_prev = ''
        self._heartbeat_comp_listener = heartbeat_comp_listener
        super(HeartbeatPoller, self).__init__(daemon=True)
    def run(self):
        while config.poller_run:

	    # Listen to the component's heartbeat
            comp_msg = self._heartbeat_comp_listener.listen()

	    # Extract a component's state
            state_component = _get_state(comp_msg)

	    # If the state changes log it
            if state_component != self._state_component_prev :
                 logger.info(comp_msg)
                 self._state_component_prev = state_component		
            config.state = 'busy'
            time.sleep(1)
