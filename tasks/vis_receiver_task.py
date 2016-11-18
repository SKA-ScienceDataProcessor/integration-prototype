#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Visibility receiver task module."""

import os
import signal
import sys

import simplejson as json
import zmq

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.vis_receiver import VisReceiver
from sip_common import logger as log

_context = zmq.Context()


def _sig_handler(signum, frame):
    sys.exit(0)


def run():
    """Task run (main) method"""
    # Read config file
    config_file = str(sys.argv[1])

    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # Load configuration.
    print('Loading config: {}'.format(config_file))
    with open(config_file) as data_file:
        config = json.load(data_file)

    # Create streams and receive SPEAD data.
    receiver = VisReceiver(config, log)
    receiver.run()


if __name__ == '__main__':
    run()

