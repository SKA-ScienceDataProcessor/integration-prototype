#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Pulsar search receiver task module.

Implements C.1.2.1.2 from the product tree.
"""

import os
import sys

import signal
import simplejson as json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sip.processor_software.pulsar_search import PulsarStart
from sip.common.logging_api import log

__author__ = 'Nijin Thykkathu'


def _sig_handler(signum, frame):
    sys.exit(0)


def main():
    """Task run method."""
    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    with open(sys.argv[1]) as f:
        config = json.load(f)

    # Starts the pulsar search ftp server
    receiver = PulsarStart(config, log)
    receiver.run()

if __name__ == '__main__':
    main()
