#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Pulsar search receiver task module.
"""
__author__ = 'Nijin Thykkathu'

import os
import signal
import sys

import simplejson as json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from processor_software.pulsar_search import PrsRun
#from sip_common import logger as log


# This is for testing purpose
def _sig_handler(signum, frame):
    sys.exit(0)


def main():
    """Task run method."""
    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    # FIXME(FD) Get configuration data - it should not happen like this.
    with open(sys.argv[1]) as f:
        config = json.load(f)

    #log.info("I am the task %%%%%%%%%%%%%%%%")
    # Create streams and receive SPEAD data. - CHANGE THIS
    receiver = PrsRun()
    receiver.run()


if __name__ == '__main__':
    main()