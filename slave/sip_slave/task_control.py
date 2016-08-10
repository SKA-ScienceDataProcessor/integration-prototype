""" This module defines the load and unload functions for controlling an
'internal' SIP task.

An internal task sends heartbeat messages to its controller.
"""

import subprocess

from sip_common import heartbeat
from sip_common import heartbeat_task
from sip_common import logger
from sip_slave import config
from sip_slave.heartbeat_poller import HeartbeatPoller

def load(task):
    """ load the task

    Some sort of task monitoring process should also be started. For
    'internal' tasks this means checking that the task has is sending
    heartbeat messages
    """
    _state_task = 'off'
    _state_task_prev = 'off'

    # Extract the port number
    port = int(task[1])

    # Start a task
    logger.info('Starting task ' + task[0])
    config.subproc = subprocess.Popen(task)

    # Create a heartbeat listener to listen for a task
    timeout_msec = 1000
    heartbeat_comp_listener = heartbeat_task.Listener(timeout_msec)
    heartbeat_comp_listener.connect('localhost', port)
    config.poller = HeartbeatPoller(heartbeat_comp_listener)
    config.poller_run = True
    config.poller.start()

def unload(task_description):
    """ Unload the task
    """

    # Stop the heartbeat poller
    config.poller_run = False

    # Kill the sub-process
    config.subproc.kill()

    # Reset state
    config.state = 'idle'
