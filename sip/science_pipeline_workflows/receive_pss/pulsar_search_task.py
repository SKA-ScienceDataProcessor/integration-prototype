# -*- coding: utf-8 -*-
"""Pulsar search receiver task module.

Implements C.1.2.1.2 from the product tree.

.. moduleauthor:: Nijin Thykkathu
"""
import logging
import os
import signal
import sys

import simplejson as json

from .pulsar_search import PulsarStart


def _sig_handler(signum, frame):  # pylint: disable=W0613
    sys.exit(0)


def main():
    """Task run method."""
    # Install handler to respond to SIGTERM
    signal.signal(signal.SIGTERM, _sig_handler)

    with open(sys.argv[1]) as fh:
        config = json.load(fh)

    # Starts the pulsar search ftp server
    os.chdir(os.path.expanduser('~'))
    receiver = PulsarStart(config, logging.getLogger())
    receiver.run()


if __name__ == '__main__':
    main()
