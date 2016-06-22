""" Function that does the actual work of loading a task
"""
import subprocess

from sip_common import heartbeat
from sip_common import heartbeat_task
from sip_common import logger
from sip_slave import config
from sip_slave.heartbeat_poller import HeartbeatPoller

def load(task):
    """ load the task
    """
    _state_task = 'off'
    _state_task_prev = 'off'

    # Assign some port to communicate with the task
    port = 6577

    # Extract the executable name from the task description
    task = task['exe']

    # Start a task
    config.subproc = subprocess.Popen([task , str(port)])
    logger.info('Starting task ' + task + ', port ' + str(port))

    # Create a heartbeat listener to listen for a task
    timeout_msec = 1000
    heartbeat_comp_listener = heartbeat_task.Listener(timeout_msec)
    heartbeat_comp_listener.connect('localhost', port)
    config.poller = HeartbeatPoller(heartbeat_comp_listener)
    config.poller_run = True
    config.poller.start()

