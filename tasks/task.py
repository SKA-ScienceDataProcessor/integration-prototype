#!/usr/bin/python3

""" Skeleton process to be started by slave

It has three states - standby, state1 and state2, toggling between
state1 and state2 in a polling loop according to the timer.

It sends heartbeat messages to the slave containing the timestamp, 
the current state and its name

"""

import sys
import os
import zmq
import time
import signal
import time
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__),'..', 'common'))

from sip_common import heartbeat_task

_context = zmq.Context()

# The state of the task
_state = 'standby'

def _sig_handler(signum, frame):
	sys.exit(0)

def run():
# Read port number
	if len(sys.argv) < 2 :
		port = 6477
	else :
		port = int(sys.argv[1])

# Define a process name to be sent to the socket
	process_name = 'PROCESS1'

    # Install handler to respond to SIGTERM
	signal.signal(signal.SIGTERM, _sig_handler)
	# Create process sender	
	process_sender = heartbeat_task.Sender(process_name, port)
	while True:
		# Create a timestamp
		ts = time.time()
		st = datetime.datetime.fromtimestamp(ts).strftime(
                        '%Y-%m-%d %H:%M:%S')
		# Change the state w.r.t. the time
		if int(time.time())%10 < 5 :
			# Doing something
			_state = 'state1'
		else :
			# Doing something else
			_state = 'state2'
		# Add current state to the heartbeat sequence
		st += ' State: '+_state + ' Component: '
		# Sent to the socket
		process_sender.send(st)
		# Wait 1 sec
		time.sleep(1)

if __name__ == '__main__':
    run()
