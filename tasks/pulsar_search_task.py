#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import signal
import sys

import simplejson as json
from processor_software.pulsar_search import PrsStart

"""Pulsar search receiver task module.

Implements C.1.2.1.2 from the product tree.
"""
__author__ = 'Nijin Thykkathu'


def _sig_handler(signum, frame):
    sys.exit(0)


def main():
    """Task run method."""
    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # FIXME(FD) Get configuration data - it should not happen like this.
    with open(sys.argv[1]) as f:
        config = json.load(f)

    # Starts the FTP Server
    receiver = PrsStart(config)
    receiver.run()


if __name__ == '__main__':
    main()
