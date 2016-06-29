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
        #_start_slave('LTS', config.slave_config['LTS'], 
        #        config.slave_status['LTS'])

        _start_slave('QA', config.slave_config['QA'], 
                config.slave_status['QA'])

def _start_slave(name, cfg, status):
    """ Start a slave controller
    """
    if cfg['type'] == 'docker':

        # Start a container if it isn't already running
        if status['state'] == '':
            _start_docker_slave(name, cfg, status)
        else:

            # Send the container a load command
            conn = rpyc.connect(status['address'], cfg['rpc_port'])
            conn.root.load()
            status['state']= 'loading'
    elif cfg['type'] == 'ssh':
        _start_ssh_slave(name, cfg, status)
    else:
       logger.error('failed to start "' + name + '": "' + cfg['type'] +
                    '" is not a known slave type')

def _start_docker_slave(name, cfg, status):
    """ Start a slave controller that is a Docker container
    """

    # Create a Docker client
    client = Client(version='1.21', base_url=cfg['engine_url'])

    # Create a container and store its id in the properties array
    image = cfg['image']
    heartbeat_port = cfg['heartbeat_port']
    rpc_port = cfg['rpc_port']
    container_id = client.create_container(image=image,
                   command=['/home/sdp/integration-prototype/slave/bin/slave', 
                            name, 
                            str(heartbeat_port),
                            str(rpc_port)
                           ],
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
    logging.getLogger('plumbum').setLevel(logging.INFO)
   
    host = cfg['host']
    ssh_host = SshMachine(host)
    rpc_port = cfg['rpc_port']
    heartbeat_port = cfg['heartbeat_port']
    import pdb
    #   pdb.set_trace()
    try:
        py3 = ssh_host['python3']
    except:
        logger.fatal('python3 not available on machine ' + ssh_host)
    logger.info('python3 is available at ' + py3.executable)
    cmd = py3['./integration-prototype/slave/bin/slave'] \
          [name][heartbeat_port][rpc_port]
    ssh_host.daemonic_popen(cmd, stdout= name + '_sip.output')
