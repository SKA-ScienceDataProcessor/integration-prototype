""" Functions for comanding a slave controller to load and unload tasks
"""

import rpyc

def load(cfg, status):
    """ Command the slave controller to load a task
    """
    conn = rpyc.connect(status['address'], status['rpc_port'])
    conn.root.load(cfg['task'])
    status['state']= 'loading'

def unload(cfg, status):
    """ Command the slave controller to unload the task
    """
    conn = rpyc.connect(status['address'], status['rpc_port'])
    conn.root.unload(cfg['task'])

