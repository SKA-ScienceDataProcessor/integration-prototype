""" Functions executed when the master controller is configured
"""
__author__ = 'David Terrett'

from docker import Client
import os
import rpyc
import threading 
from plumbum import SshMachine
import logging

from sip_common import logger

from sip_master import config

class Configure(threading.Thread):
    """ Does the actual work of configuring the system
    """
    def __init__(self):
        super(Configure, self).__init__()

    def run(self):
        """ Thread run routine
        """
        logger.trace('starting configuration')
        
        # Start the local telescope state application
        _start_slave('LTS', config.slave_config['LTS'], 
                config.slave_status['LTS'])

        _start_slave('QA', config.slave_config['QA'], 
                config.slave_status['QA'])

def _start_slave(name, cfg, status):
    """ Start a slave controller
    """

    # Start a container if it isn't already running
    if status['state'] == '':
        if cfg['type'] == 'docker':
            _start_docker_slave(name, cfg, status)
        elif cfg['type'] == 'ssh':
            _start_ssh_slave(name, cfg, status)
        else:
            logger.error('failed to start "' + name + '": "' + cfg['type'] +
                    '" is not a known slave type')
    else:
        # Send the container a load command
        conn = rpyc.connect(status['address'], cfg['rpc_port'])
        conn.root.load(cfg['task'])
        status['state']= 'loading'

def _start_docker_slave(name, cfg, status):
    """ Start a slave controller that is a Docker container
    """
    # Improve logging soon!
    logging.getLogger('requests').setLevel(logging.DEBUG)

    # Create a Docker client
    client = Client(version='1.21', base_url=cfg['engine_url'])

    # Create a container and store its id in the properties array
    image = cfg['image']
    heartbeat_port = cfg['heartbeat_port']
    rpc_port = cfg['rpc_port']
    task_control_module = cfg['task_control_module']
    container_id = client.create_container(image=image, 
                   command=['/home/sdp/integration-prototype/slave/bin/slave', 
                            name, 
                            str(heartbeat_port),
                            str(rpc_port),
                            task_control_module,
                           ],
                   environment={"SIP_HOSTNAME":os.environ['SIP_HOSTNAME']},
		   volumes=['/home/sdp/tasks/'],
		   host_config=client.create_host_config(binds={
        		os.getcwd()+'/tasks': {
            		'bind': '/home/sdp/tasks/',
            		'mode': 'rw',
        		}
                   }))['Id']

    # Start it
    client.start(container_id)
    info = client.inspect_container(container_id)
    ip_address = info['NetworkSettings']['IPAddress']
    status['address'] = ip_address
    status['state'] = 'starting'
    status['new_state'] = 'starting'
    status['container_id'] = container_id
    status['timeout counter'] = cfg['timeout']
    logger.info(name + ' started in container ' + container_id + ' at ' +
                ip_address)

    # Connect the heartbeat listener to the address it is sending heartbeats
    # to.
    config.heartbeat_listener.connect(ip_address, heartbeat_port)

def _start_ssh_slave(name, cfg, status):
    """ Start a slave controller that is a SSH client
    """
    # Improve logging setup!!!
    logging.getLogger('plumbum').setLevel(logging.DEBUG)
   
    #host = cfg['host']
    host = config.resource.allocate_host(name, {'launch_protocol': 'ssh'}, {})
    sip_root = config.resource.sip_root(host)
    ssh_host = SshMachine(host)
    rpc_port = cfg['rpc_port']
    heartbeat_port = cfg['heartbeat_port']
    task_control_module = cfg['task_control_module']
    import pdb
    #   pdb.set_trace()
    try:
        py3 = ssh_host['python3']
    except:
        logger.fatal('python3 not available on machine ' + ssh_host)
    logger.info('python3 is available at ' + py3.executable)
    cmd = py3[os.path.join(sip_root, 'slave/bin/slave')] \
          [name][heartbeat_port][rpc_port][task_control_module]
    ssh_host.daemonic_popen(cmd, stdout= name + '_sip.output')

    status['address'] = host
    status['state'] = 'starting'
    status['new_state'] = 'starting'
    status['timeout counter'] = cfg['timeout']
    logger.info(name + ' started on ' + host)

    # Connect the heartbeat listener to the address it is sending heartbeats
    # to.
    config.heartbeat_listener.connect(host, heartbeat_port)

