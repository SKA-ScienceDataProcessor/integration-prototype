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

def capability(type):
    """ Configure a capability
    """
    global connection_
    return connection_.root.capability('localhost', type)

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
