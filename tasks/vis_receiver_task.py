#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Visibility receiver task module.

Implements C.1.2.1.4 from the product tree.
"""

import os
import signal
import sys

import simplejson as json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from processor_software.vis_receiver import VisReceiver
from sip_common import logger as log


def _sig_handler(signum, frame):
    sys.exit(0)


def main():
    """Task run method."""
    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # FIXME(FD) Get configuration data - it should not happen like this.
    with open(sys.argv[1]) as f:
        config = json.load(f)

    # Create streams and receive SPEAD data.
    receiver = VisReceiver(config, log)
    receiver.run()


if __name__ == '__main__':
    main()

