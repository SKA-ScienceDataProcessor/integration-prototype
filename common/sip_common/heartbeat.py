""" This defines the SIP API for sending and receiving heartbeat messages
"""
__author__ = 'David Terrett'

import string
import zmq

_context = zmq.Context()

class Sender:
    """ Class for sending heartbeat messages
    """
    def __init__(self, name, port = '6478'):

        # Create a publish socket and bind it to port 6478 
        self._socket = _context.socket(zmq.PUB)
        self._socket.bind('tcp://*:' + port)

        # Store our name
        self._name = name

    def send(self, status):
        """ Send a heartbeat message """
        self._socket.send_string(self._name + ':' + status)

class Listener:
     """ Class for listening for heartbeat messages
     """
     def __init__(self, timeout):
        self._timeout = timeout

        # Create a subscriber socket that excepts all messages
        self._socket = _context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')

     def connect(self, host, port='6478'):
        """ Binds to a publisher
        
        Can be called multiple times to listen to more than one publisher
        """
        self._socket.connect('tcp://' + host + ':' + port)

     def listen(self):
        """ Listens for heartbeat messages

        Returns the name of the sender of the heartbeat and the status or 
        an empty string if no message is received
        """
        if self._socket.poll(self._timeout) != 0:
            msg = self._socket.recv_string()
            return msg.split(':')
        return ''
       
