""" Function that does the actual work of unloading a task
"""
import subprocess

from sip_slave import config

def unload():
    """ Unload the task
    """

    # Stop the poller
    config.poller_run = False

    # Kill the sub-process
    config.subproc.kill()

    # Reset state
    config.state = 'idle'
