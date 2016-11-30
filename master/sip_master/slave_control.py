""" Functions for starting and stopping slave controllers
"""
__author__ = 'David Terrett'

from docker import Client
import logging
import netifaces
import os
from plumbum import SshMachine
from pyroute2 import IPRoute
import rpyc
import socket
import time

from sip_common import logger

from sip_master import config
from sip_master import task_control
from sip_master.slave_states import SlaveControllerSM


def _find_route_to_logger(host):
    """ Figures out what the IP address of the logger is on 'host'
    """
    addr = socket.gethostbyname(host)
    ip = IPRoute()
    r = ip.get_routes(dst=addr, family=socket.AF_INET)
    for x in r[0]['attrs']:
        if x[0] == 'RTA_PREFSRC':
            return x[1]


def start(name, type):
    """Start a slave controller."""

    # Check that the type exists
    if type not in config.slave_config:
        raise RuntimeError('"{}" is not a known task type'.format(type))

    # Create an entry in the slave status dictionary if one doesn't already
    # exist
    if not name in config.slave_status:
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

        # Initialise the task status
        slave_status['timeout counter'] = slave_config['timeout']

        # Connect the heartbeat listener to the address it is sending heartbeats
        # to.
        config.heartbeat_listener.connect(slave_status['address'],
                                          slave_status['heartbeat_port'])

        # RPyC connected when the first heartbeat is received
        # (in heartbeat_listener.py).
    else:
        # Otherwise a slave was running (but no task) so we can just instruct
        # the slave to start the task.
        slave_status['task_controller'].start(name, slave_config, slave_status)
        slave_status['state'].post_event(['load sent'])


def _start_docker_slave(name, type, cfg, status):
    """ Start a slave controller that is a Docker container

        NB This only works on localhost
    """
    # Improve logging soon!
    logging.getLogger('requests').setLevel(logging.DEBUG)

    # Create a Docker client
    client = Client(version='1.21', base_url=cfg['engine_url'])

    # Create a container and store its id in the properties array
    host = config.resource.allocate_host(name,
            {'launch_protocol': 'docker'}, {})
    image = cfg['docker_image']
    heartbeat_port = config.resource.allocate_resource(name, "tcp_port")
    rpc_port = config.resource.allocate_resource(name, "tcp_port")
    task_control_module = cfg['task_control_module']['name']
    logger_address = \
            netifaces.ifaddresses('docker0')[netifaces.AF_INET][0]['addr']
    container_id = client.create_container(image=image,
                   command=['/home/sdp/integration-prototype/slave/bin/slave',
                            name,
                            str(heartbeat_port),
                            str(rpc_port),
                            logger_address,
                            task_control_module,
                           ]
                   )['Id']

    # Start it
    client.start(container_id)

    # Fill in the docker specific entries in the status dictionary
    info = client.inspect_container(container_id)
    ip_address = info['NetworkSettings']['IPAddress']
    status['address'] = ip_address
    status['container_id'] = container_id

    # Fill in the generic entries
    status['rpc_port'] = rpc_port
    status['heartbeat_port'] = heartbeat_port
    status['sip_root'] = '/home/sdp/integration-prototype'
    logger.info('"{}" (type {}) started in container {} at {}'.format(
            name, type, container_id, ip_address))


def _start_ssh_slave(name, type, cfg, status):
    """ Start a slave controller that is a SSH client
    """
    # Improve logging setup!!!
    logging.getLogger('plumbum').setLevel(logging.DEBUG)

    # Find a host that supports ssh
    host = config.resource.allocate_host(name, {'launch_protocol': 'ssh'}, {})

    # Get the root of the SIP installation on that host
    sip_root = config.resource.sip_root(host)

    # Allocate ports for heatbeat and the RPC interface
    heartbeat_port = config.resource.allocate_resource(name, "tcp_port")
    rpc_port = config.resource.allocate_resource(name, "tcp_port")

    # Get the task control module to use for this task
    task_control_module = cfg['task_control_module']['name']

    # Get the address of the logger (as seen from the remote host)
    logger_address = _find_route_to_logger(host)

    ssh_host = SshMachine(host)
    try:
        py3 = ssh_host['python3']
    except:
        logger.fatal('python3 not available on machine {}'.format(ssh_host))
    logger.info('python3 is available at {}'.format(py3.executable))

    # Construct the command line to start the slave
    cmd = py3[os.path.join(sip_root, 'slave/bin/slave')] \
          [name][heartbeat_port][rpc_port][logger_address][task_control_module]
    ssh_host.daemonic_popen(cmd, stdout='{}_sip.output'.format(name))

    # Fill in the status dictionary
    status['address'] = host
    status['rpc_port'] = rpc_port
    status['heartbeat_port'] = heartbeat_port
    status['sip_root'] = sip_root
    logger.info('{} (type {}) started on {}'.format(name, type, host))


def stop(name, status):
    """ Stop a slave controller
    """
    status['task_controller'].shutdown()
    if config.slave_config[status['type']]['launch_policy'] == 'docker':
        _stop_docker_slave(name, status)

    # Release the resources allocated to this task.
    config.resource.release_host(name)

    # Send the stop sent event to the state machine
    status['state'].post_event(['stop sent'])


def _stop_docker_slave(name, status):
    """ Stop a docker based slave controller
    """

    # Create a Docker client
    base_url = config.slave_config[status['type']]['engine_url']
    client = Client(version='1.21', base_url=base_url)

    # Stop the container and remove the container
    client.stop(status['container_id'])
    client.remove_container(status['container_id'])

