# coding: utf-8
"""Functions for starting and stopping slave controllers."""

__author__ = 'David Terrett'

import logging
import os
import socket
import sys

from sip.common.logging_api import log
from sip.common.paas import TaskStatus
#from sip.common.docker_paas import DockerPaas as Paas
from sip.common.marathon_paas import MarathonPaas as Paas
from sip.master.config import create_slave_status
from sip.master.config import slave_status
from sip.master.config import slave_config
from sip.master import task_control
from sip.master import slave_states
from sip.master.slave_states import SlaveControllerSM

# This is the port used by the slave for its RPC interface. It is mapped to
# some ephemeral port on the local host by Docker.
rpc_port_ = 6666

def start(name, type):
    """Starts a slave controller."""

    log.info('Starting slave (name={}, type={})'.format(name, type))

    # Create an entry in the slave status dictionary if one doesn't already
    # exist
    log.info('Creating new slave, name={}'.format(name))
    task_controller = task_control.SlaveTaskControllerRPyC()
    state_machine = SlaveControllerSM(name, type, task_controller)
    create_slave_status(name, type, task_controller,
            state_machine)

    # Check that the slave isn't already running
    status = slave_status(name)
    config = slave_config(name)
    current_state = status['state'].current_state()
    log.debug('State of slave {} is {}'.format(name, current_state))
    if current_state == 'Starting' or current_state == 'Running':
        raise RuntimeError('Error starting {}: task is already {}'.format(
                name, current_state))

    # Start a slave if it isn't already running
    if current_state == 'Exited' or current_state == 'Init' or (
            current_state == 'Unknown'):

        # Start the slave
        if config['launch_policy'] == 'docker':
            _start_docker_slave(name, type, config, status)
        elif config['launch_policy'] == 'marathon':
            _start_marathon_slave(name, type, config, status)
        else:
            raise RuntimeError(
                    'Error starting "{}": {} is not a known slave launch '
                    'policy'.format(name, config['launch_policy']))

        log.debug('Started slave! (name={}, type={})'.format(name, type))
    status['restart'] = True


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
    task_control_module = cfg['task_control_module']['name']
    _cmd = ['python3', '-m', 'sip.slave',
            name,
            str(rpc_port_),
            task_control_module,
            ]

    # Start it
    paas = Paas()
    descriptor = paas.run_service(name, 'sip', [rpc_port_], _cmd)

    # Attempt to connect the controller
    try:
        (hostname, port) = descriptor.location(rpc_port_)
        status['task_controller'].connect(hostname, port)
    except:
        pass

    # Fill in the generic entries in the status dictionary
    status['sip_root'] = '/home/sdp/integration-prototype'
    status['descriptor'] = descriptor

    log.info('"{}" (type {}) started'.format(name, type))


def stop(name, status):
    """Stops a slave controller."""
    log.info('stopping task {}'.format(name))
    status['task_controller'].shutdown()
    if slave_config(name)['launch_policy'] == 'docker':
        _stop_docker_slave(name, status)
    elif slave_config(name)['launch_policy'] == 'marathon':
        _stop_marathon_slave(name, status)


def _stop_docker_slave(name, status):
    """Stops a docker based slave controller."""

    log.info('stopping slave controller {}'.format(name))
    paas = Paas()
    descriptor = paas.find_task(name)
    if descriptor:
        descriptor.delete()
    else:
        log.info('task {} not found'.format(name))

def reconnect(name, descriptor):
    """ Reconnects to an existing slave service

    This rebuild the internal data structure in order to re-establish
    the connection to a slave that is already running. This makes it
    possible to to restart the master controller.
    """
    # Create a task controller for it
    task_controller = task_control.SlaveTaskControllerRPyC()
    #(hostname, port) = descriptor.location(rpc_port_)
    (hostname, port) = descriptor.location()
    #task_controller.connect(hostname, port)
    task_controller.connect(hostname, port[0])

    # Create a state machine for it with an intial state corresponding to
    # the state of the slave.
    service_state = descriptor.status()
    if service_state == TaskStatus.RUNNING:

        # Assuming that a RUNNING service is busy. If it isn't it will
        # get restarted when the state machine transitions to Ruuning_idle
        # as a result of the event from the slave poller.
        sm = SlaveControllerSM(name, name, task_controller,
                init=slave_states.Running_busy)
    elif service_state == TaskStatus.EXITED:
        sm = SlaveControllerSM(name, name, task_controller,
                init=slave_states.Exited)
    elif service_state == TaskStatus.ERROR:
        sm = SlaveControllerSM(name, name, task_controller,
                init=slave_states.Error)
    elif service_state == TaskStatus.UNKNOWN:
        sm = SlaveControllerSM(name, name, task_controller,
                init=slave_states.Unknown)
    elif service_state == TaskStatus.STARTING:
        sm = SlaveControllerSM(name, name, task_controller,
                init=slave_states.Starting)

    # Create a config status
    create_slave_status(name, name, task_controller, sm)
    status = slave_status(name)

    # Set the restart flag
    status['restart'] = True

    # Set a descriptor for the service
    status['descriptor'] = descriptor


def _start_marathon_slave(name, type, cfg, status):
    """Starts a slave controller that is a Docker container.

    NB This only works on localhost
    """
    # Improve logging soon!
    req_log = logging.getLogger('requests')
    req_log.setLevel(logging.WARN)
    req_log.addHandler(logging.StreamHandler(sys.stdout))

    log.info('Starting Marathon slave (name={}, type={})'.format(name, type))

    # Create a service. The paas takes care of the host and ports so
    # we can use any ports we like in the container and they will get
    # mapped to free ports on the host.
    task_control_module = cfg['task_control_module']['name']


    _cmd = ['python3', '/home/vlad/software/SKA/integration-prototype/sip/slave/slavemain.py',
            name,
            str(rpc_port_),
            task_control_module,
            ]

    # Start it
    paas = Paas()
    descriptor = paas.run_service(name, 'siptest', [rpc_port_], _cmd)


    # Attempt to connect the controller
    try:
        (hostname, port) = descriptor.location()
        status['task_controller'].connect(hostname, port[0])
    except:
        pass


    # Fill in the generic entries in the status dictionary
    (host, ports) = descriptor.location()
 #   status['rpc_port'] = ports[0]
    status['sip_root'] = '/home/vlad/software/SKA/integration-prototype'
    status['descriptor'] = descriptor

    log.info('"{}" (type {}) started'.format(name, type))


def _stop_marathon_slave(name, status):
    """Stops a marathon based slave controller."""

    log.info('stopping slave controller {}'.format(name))
    paas = Paas()
    descriptor = paas.find_task(name)
    descriptor.delete()


