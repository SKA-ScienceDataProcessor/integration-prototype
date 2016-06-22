""" Function ithat does the actual work of loading a component
"""
import subprocess

from sip_common import heartbeat
from sip_common import heartbeat_component
from sip_common import logger
from sip_slave import config
from sip_slave.heartbeat_poller import HeartbeatPoller

def load(task):
    """ load the task
    """
    _state_component = 'off'
    _state_component_prev = 'off'

    # Assign some port to communicate with the component
    port = 6577

    # Extract the executable name from the task description
    component = task['exe']

    # Start a component
    config.subproc = subprocess.Popen([component , str(port)])
    logger.info('Starting component ' + component + ', port ' + str(port))

    # Create a heartbeat listener to listen for a component
    timeout_msec = 1000
    heartbeat_comp_listener = heartbeat_component.Listener(timeout_msec)
    heartbeat_comp_listener.connect('localhost', port)
    config.poller = HeartbeatPoller(heartbeat_comp_listener)
    config.poller_run = True
    config.poller.start()

