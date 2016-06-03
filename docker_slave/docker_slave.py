#!/usr/bin/python3

""" Skeleton slave controller for use in a Docker container

All it does is send heartbeat messages to MC.

It also can start a component, currently /home/sdp/components/component.py,
monitor it's hearbeat messages, extract the component's state and write 
into a system log when the state changes.

The default behaviour is to start the component automatically when the slave starts,
this will be replaced later.

A handler for SIGTERM is set up that just exits because that is what
'Docker stop' sends.
"""

import signal
import sys
import time
import copy

sys.path.append('/home/sdp/lib/python')
import heartbeat
import heartbeat_component
import logger

import subprocess

def _sig_handler(signum, frame):
    sys.exit(0)
"""
The function _get_state(msg) extracts the state from the heartbeat message
"""
def _get_state(msg):
    tokens = msg.split(" ")
    if len(tokens) < 4 :
         tokens = [' ', ' ', ' ', 'off', ' ', ' ']
    return tokens[3]	

def run():
    _state_component = 'off'
    _state_component_prev = 'off'
    name = sys.argv[1]
    logger.info('Slave controller "' + name + '" starting')

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # Assign some port to communicate with the component
    port = 6577

    # Start a component
    component = '/home/sdp/components/component.py'
    subprocess.Popen([component , str(port)])
    logger.info('Starting component ' + component + ', port ' + str(port))

    # Create a heartbeat listener to listen for a component
    timeout_msec = 1000
    heartbeat_comp_listener = heartbeat_component.Listener(timeout_msec)
    heartbeat_comp_listener.connect('localhost', str(port))

    # Create a heartbeat sender to MC
    heartbeat_sender = heartbeat.Sender(name)

    # Start polling loop
    while True:
	# Listen to the component's heartbeat
        comp_msg=heartbeat_comp_listener.listen()
	# Extract a component's state
        _state_component = _get_state(comp_msg)
	# If the state cganges log it
        if _state_component != _state_component_prev :
             logger.info(comp_msg)
             _state_component_prev = _state_component		
        heartbeat_sender.send()
        time.sleep(1)

if __name__ == '__main__':
    run()
