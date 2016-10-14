""" Simple rpc client for sending commands to the SIP
"""
__author__ = 'David Terrett'

import rpyc
import sys

connection_ = None

def connect(host='localhost', port=12345):
    """ Connect to SIP
    """
    global connection_
    connection_ = rpyc.connect(host, port)

def disconnect():
    """ Disconnect from SIP
    """
    global connection_
    connection_ = None

def online():
    """ Set SIP online
    """
    global connection_
    return connection_.root.online()

def capability(name, type):
    """ Configure a capability

        :param name: A name for the capability
        :param type: The capability type

    The name must be unique (i.e. different from all the task names
    defined in the slave map). The type corresponds to one of the task
    names in the map (.e.g. 'ingest').
    """
    global connection_
    return connection_.root.capability(name, type)

def offline():
    """ Set SIP offline
    """
    global connection_
    return connection_.root.offline()

def shutdown():
    """ Shutdown the SIP
    """
    global connection_
    return connection_.root.shutdown()

def state():
    return connection_.root.get_current_state()
