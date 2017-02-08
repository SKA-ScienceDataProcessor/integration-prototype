# coding: utf-8
"""Logging aggregator service script.

Receives messages from other SIP modules via ZMQ. This service is currently
started by the Master Controller main() (master/sip_master/main.py).

Notes:
    - Needs configuration for SUB port, currently using the default
      TCP logging port.
    - Needs a REST / RPC (and CLI) API allowing configuring of
      filters and handlers.

.. moduleauthor:: Benjamin Mort <benjamin.mort@oerc.ox.ac.uk>
"""
import multiprocessing
import os
import signal
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from sip.common.logging_aggregator import LogAggregator


def signal_handler(signum, frame):
    """signal handler.

    Args:
        signum: The signal number received.
        frame: The current stack frame.
    """
    print('Logging Aggregator (pid: {}) received SIGINT.'.
          format(multiprocessing.current_process().pid))
    sys.exit(0)


def main():
    """Create and start the log aggregator"""
    signal.signal(signal.SIGINT, signal_handler)
    print('Starting Logging Aggregator service (pid: {}).'.format(os.getpid()))
    log = LogAggregator()
    log.daemon = True
    log.start()
    log.join()
    print('Terminating Logging Aggregator service (pid: {}).'.
          format(os.getpid()))

if __name__ == '__main__':
    main()
