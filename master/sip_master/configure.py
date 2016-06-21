""" Functions executed when the master controller is configured
"""
__author__ = 'David Terrett'

from docker import Client
import os
import rpyc
import threading 

from sip_common import logger

from sip_master.slave_map import slave_config
from sip_master.slave_map import slave_status
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
        _start_slave('LTS', slave_config['LTS'], slave_status['LTS'])

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
                            heartbeat_port,
                            rpc_port
                           ],
		   volumes=['/home/sdp/components/'],
		   host_config=client.create_host_config(binds={
        		os.getcwd()+'/components': {
            		'bind': '/home/sdp/components/',
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
