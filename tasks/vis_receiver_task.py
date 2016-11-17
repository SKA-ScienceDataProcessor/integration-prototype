#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import signal
import sys
import simplejson as json
import zmq

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.vis_receiver import VisReceiver
from sip_common import heartbeat_task
from sip_common import logger as log

_context = zmq.Context()


def _sig_handler(signum, frame):
    sys.exit(0)


def run():
    print("Current directory: ", os.getcwd())
    # Read heartbeat port number
    if len(sys.argv) < 2:
        heartbeat_port = 6477
    else:
        heartbeat_port = int(sys.argv[1])

    # Read config file
    config_file = str(sys.argv[2])

    # Define a process name to be sent to the socket
    process_name = 'VIS_RECEIVER'

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)
    # Create process sender
    process_sender = heartbeat_task.Sender(process_name, heartbeat_port)

    # Load configuration.
    print('Loading config: {}'.format(config_file))
    with open(config_file) as data_file:
        config = json.load(data_file)

    # Create streams and receive SPEAD data.
    receiver = VisReceiver(config, log, process_sender)
    receiver.run()

    process_sender.send("Done")


if __name__ == '__main__':
    run()
