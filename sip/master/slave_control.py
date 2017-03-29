# coding: utf-8
"""Functions for starting and stopping slave controllers."""

__author__ = 'David Terrett'

import logging
import os
import socket
import sys

from sip.common.logging_api import log
from sip.common.docker_paas import DockerPaas as Paas
from sip.master import config
from sip.master import task_control
from sip.master.slave_states import SlaveControllerSM


def start(name, type):
    """Starts a slave controller."""

    # Check that the type exists
    if type not in config.slave_config:
        raise RuntimeError('"{}" is not a known task type'.format(type))

    log.info('Starting slave (name={}, type={})'.format(name, type))

    # Create an entry in the slave status dictionary if one doesn't already
    # exist
    if name not in config.slave_status:
        log.info('Creating new slave, name={}'.format(name))
        task_controller = task_control.SlaveTaskControllerRPyC()
        config.slave_status[name] = {
                'type': type,
                'task_controller': task_controller,
                'state': SlaveControllerSM(name, type, task_controller),
                'descriptor': None}

    # Check that the slave isn't already running
    slave_status = config.slave_status[name]  # Shallow copy (i.e. reference)
    slave_config = config.slave_config[type]  # Shallow copy (i.e. reference)
    current_state = slave_status['state'].current_state()
    log.debug('State of slave {} is {}'.format(name, current_state))
    if current_state == 'Starting' or current_state == 'Running':
        raise RuntimeError('Error starting {}: task is already {}'.format(
                name, current_state))

    # Start a slave if it isn't already running
    if current_state == 'Exited' or current_state == 'Init' or (
            current_state == 'Unknown'):

        # Start the slave
        if slave_config['launch_policy'] == 'docker':
            _start_docker_slave(name, type, slave_config, slave_status)
        else:
            raise RuntimeError(
                    'Error starting "{}": {} is not a known slave launch '
                    'policy'.format(name, slave_config['launch_policy']))

        log.debug('Started slave! (name={}, type={})'.format(name, type))
    else:
        # Otherwise a slave was running (but no task) so we can just instruct
        # the slave to start the task.
        slave_status['task_controller'].start(name, slave_config, slave_status)
        slave_status['state'].post_event(['load sent'])


def _start_docker_slave(name, type, cfg, status):
    """Starts a slave controller that is a Docker container.

    NB This only works on localhost
    """
    # Improve logging soon!
    req_log = logging.getLogger('requests')
    req_log.setLevel(logging.WARN)
    req_log.addHandler(logging.StreamHandler(sys.stdout))

    log.info('Starting Docker slave (name={}, type={})'.format(name, type))

    # Create a service. The paas takes care of the host and ports so
    # we can use any ports we like in the container and they will get
    # mapped to free ports on the host.
    image = cfg['docker_image']
    rpc_port = 6666
    task_control_module = cfg['task_control_module']['name']
    _cmd = ['python3', '-m', 'sip.slave',
            name,
            str(rpc_port),
            '0',
            task_control_module,
            ]

    # Start it
    paas = Paas()
    descriptor = paas.run_service(name, 'sip', [rpc_port], _cmd)

    # Fill in the generic entries in the status dictionary
    (host, ports) = descriptor.location()
    status['rpc_port'] = ports[rpc_port]
    status['sip_root'] = '/home/sdp/integration-prototype'
    status['descriptor'] = descriptor

    log.info('"{}" (type {}) started'.format(name, type))


def stop(name, status):
    """Stops a slave controller."""
    log.info('stopping task {}'.format(name))
    status['task_controller'].shutdown()
    if config.slave_config[status['type']]['launch_policy'] == 'docker':
        _stop_docker_slave(name, status)

def _stop_docker_slave(name, status):
    """Stops a docker based slave controller."""

    log.info('stopping slave controller {}'.format(name))
    paas = Paas()
    descriptor = paas.find_task(name)
    descriptor.delete()

