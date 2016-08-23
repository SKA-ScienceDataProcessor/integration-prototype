#!/usr/bin/python3

""" Skeleton execution engine

It has three states - starting, running and and finished. It starts in
starting, moves to running after 10s and then to finished after some
time specified on the command line

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
from sip_common import logger

_context = zmq.Context()

def _sig_handler(signum, frame):
    sys.exit(0)

def run():

    # The state of the task
    _state = 'starting'

    # Read port number
    if len(sys.argv) < 2 :
       	port = 6477
    else :
       	port = int(sys.argv[1])
    if len(sys.argv) < 3 :
       	run_time = 60
    else :
       	run_time = int(sys.argv[2])

    # Define a process name to be sent to the socket
    process_name = 'exec_eng'

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)
    # Create process sender	
    process_sender = heartbeat_task.Sender(process_name, port)
    start_time = time.time()
    while _state != 'finished':

        # Create a timestamp
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

	# Change the state w.r.t. the time
        if time.time() - start_time > run_time + 10.0:
            logger.info('exec engine has finished')
            _state = 'finished'
        elif time.time() - start_time > 10.0 :
            if _state == 'starting':
                logger.info('exec engine now busy')
            _state = 'busy'

        # Add current state to the heartbeat sequence
        st += ' State: ' + _state + ' Component: '

        # Sent to the socket
        process_sender.send(st)

        # Wait 1 sec
        time.sleep(1)

if __name__ == '__main__':
    run()




