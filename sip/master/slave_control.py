# coding: utf-8
"""Functions for starting and stopping slave controllers."""

__author__ = 'David Terrett'

import logging
import netifaces
import os
import socket
import sys

from docker import APIClient as Client
from plumbum import SshMachine
from pyroute2 import IPRoute

from sip.common.logging_api import log
from sip.common.docker_paas import DockerPaas as Paas
from sip.master import config
from sip.master import task_control
from sip.master.slave_states import SlaveControllerSM

def _find_route_to_logger(host):
    """Figures out what the IP address of the logger is on 'host'."""
    addr = socket.gethostbyname(host)
    ip = IPRoute()
    r = ip.get_routes(dst=addr, family=socket.AF_INET)
    for x in r[0]['attrs']:
        if x[0] == 'RTA_PREFSRC':
            return x[1]


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
                'timeout counter': 0}

    # Check that the slave isn't already running
    slave_status = config.slave_status[name]  # Shallow copy (i.e. reference)
    slave_config = config.slave_config[type]  # Shallow copy (i.e. reference)
    current_state = slave_status['state'].current_state()
    if current_state == 'loading' or current_state == 'busy':
        raise RuntimeError('Error starting {}: task is already {}'.format(
                name, current_state))

    # Start a slave if it isn't already running
    if current_state == '_End' or current_state == 'Starting':

        # Start the slave
        if slave_config['launch_policy'] == 'docker':
            _start_docker_slave(name, type, slave_config, slave_status)
        elif slave_config['launch_policy'] == 'ssh':
            _start_ssh_slave(name, type, slave_config, slave_status)
        else:
            raise RuntimeError(
                    'Error starting "{}": {} is not a known slave launch '
                    'policy'.format(name, slave_config['launch_policy']))

        log.debug('Started slave! (name={}, type={})'.format(name, type))
        # Initialise the task status
        slave_status['timeout counter'] = slave_config['timeout']

        # Connect the (MC?) heartbeat listener to the address it is
        # sending heartbeats to.
        config.heartbeat_listener.connect(slave_status['address'],
                                          slave_status['heartbeat_port'])
        log.debug('Connected to {}:{} for heartbeats'.format(
                    slave_status['address'],
                    slave_status['heartbeat_port']))

        # RPyC connected when the first heartbeat is received
        # (in heartbeat_listener.py).
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

    # Create a Docker client
    client = Client(version='1.21', base_url=cfg['engine_url'])

    # Create a service. The paas takes care of the host and ports so
    # we can use any ports we like in the container and they will get
    # mapped to free ports on the host.
    image = cfg['docker_image']
    rpc_port = 6666
    heartbeat_port = 6667
    task_control_module = cfg['task_control_module']['name']
    _cmd = ['python3', '-m', 'sip.slave',
            name,
            str(heartbeat_port),
            str(rpc_port),
            '0',
            task_control_module,
            ]

    # Start it
    paas = Paas()
    descriptor = paas.run_service(name, 'sip', [rpc_port, heartbeat_port], _cmd)

    # Fill in the docker specific entries in the status dictionary
    status['address'] = descriptor.hostname
    status['container_id'] = descriptor.ident

    # Fill in the generic entries
    status['rpc_port'] = descriptor.ports[rpc_port]
    status['heartbeat_port'] = descriptor.ports[heartbeat_port]
    status['sip_root'] = '/home/sdp/integration-prototype'
    log.info('"{}" (type {}) started'.format(name, type))


def _start_ssh_slave(name, type, cfg, status):
    """Starts a slave controller that is a SSH client."""
    # FIXME(BM) need to look into how capture plumbum messages.
    pb_log = logging.getLogger('plumbum')
    pb_log.setLevel(logging.INFO)
    pb_log.addHandler(logging.StreamHandler(sys.stdout))

    log.info('Starting SSH slave (name={}, type={})'.format(name, type))

    # Find a host that supports ssh
    host = config.resource.allocate_host(name, {'launch_protocol': 'ssh'}, {})

    # Get the root of the SIP installation on that host
    sip_root = config.resource.sip_root(host)
    sip_root = os.path.normpath(os.path.join(sip_root, '..'))
    log.debug('SSH SIP root: {}'.format(sip_root))

    # Allocate ports for heatbeat and the RPC interface
    heartbeat_port = config.resource.allocate_resource(name, "tcp_port")
    rpc_port = config.resource.allocate_resource(name, "tcp_port")

    # Get the task control module to use for this task
    task_control_module = cfg['task_control_module']['name']

    # Get the address of the logger (as seen from the remote host)
    logger_address = _find_route_to_logger(host)

    log.debug('Getting SSH slave interface.')
    ssh_host = SshMachine(host)
    try:
        py3 = ssh_host['python3']
    except:
        log.fatal('Python3 not available on machine {}'.format(ssh_host))

    log.info('Python3 is available on {} at {}'.format(ssh_host,
                                                       py3.executable))

    # Construct the command line to start the slave
    home_dir = os.path.expanduser('~')
    output_file = os.path.join(home_dir, '{}_sip.output'.format(name))
    cmd = py3['-m']['sip.slave'] \
          [name][heartbeat_port][rpc_port][logger_address][task_control_module]
    log.debug('SSH command = {}'.format(cmd))
    ssh_host.daemonic_popen(cmd, cwd=sip_root, stdout=output_file)

    # Fill in the status dictionary
    status['address'] = host
    status['rpc_port'] = rpc_port
    status['heartbeat_port'] = heartbeat_port
    status['sip_root'] = sip_root
    log.info('{} (type {}) started on {}'.format(name, type, host))


def stop(name, status):
    """Stops a slave controller."""
    status['task_controller'].shutdown()
    if config.slave_config[status['type']]['launch_policy'] == 'docker':
        _stop_docker_slave(name, status)

    # Release the resources allocated to this task.
    #config.resource.release_host(name)

    # Send the stop sent event to the state machine
    status['state'].post_event(['stop sent'])


def _stop_docker_slave(name, status):
    """Stops a docker based slave controller."""

    paas = Paas()
    descriptor = paas.find_task(name)
    descriptor.delete()

