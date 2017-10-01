# coding: utf-8
""" This is a trivial test task

It sleeps for a time specified by the first command line argument (seconds)
and then exits with a status specified by the second.
"""
import logging
import sys
import time


def main():
    """ Mock task used by the Docker Swarm PaaS unittests

    Exits after a specified delay with the specified exit code.
    """
    timeout = float(sys.argv[1])
    exit_status = int(sys.argv[2])

    log = logging.getLogger(__name__)
    log.debug('Starting mock task, timeout = %.2fs, exit status = %i',
              timeout, exit_status)

    start_time = time.time()
    try:
        while time.time() - start_time <= timeout:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    log.debug('Mock task exiting after %.2fs with status = %i',
              time.time() - start_time, exit_status)

    sys.exit(exit_status)


if __name__ == '__main__':
    # LOG = logging.getLogger()
    # LOG.setLevel(logging.DEBUG)
    # LOG.addHandler(logging.StreamHandler())
    main()
