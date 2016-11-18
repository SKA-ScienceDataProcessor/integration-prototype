import zmq

""" This defines the SIP API for sending and receiving messages
    to and from a task started by slave.
    It is based on heartbeat module, the main difference is the port number
    which is not fixed but a constructor's parameter.

    The heartbeat message is constructed using an arbitary string (usually
    a timestamp plus a state of the task) and the task's name.
"""

_context = zmq.Context()


class Sender:
    """ Class for sending heartbeat messages
    """

    def __init__(self, name, port):
        # Create a publish socket and bind it to the specified port
        self._socket = _context.socket(zmq.PUB)
        self._socket.bind('tcp://*:' + str(port))

        # Store our name
        self._name = name

    def send(self, st):
        """ Send a heartbeat message inc a timestamp"""
        self._st = st + self._name
        self._socket.send_string(self._st)


class Listener:
    """ Class for listening for heartbeat messages
     """

    def __init__(self, timeout):
        self._timeout = timeout

        # Create a subscriber socket that excepts all messages
        self._socket = _context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def connect(self, host, port):
        """ Binds to a publisher
        
        Can be called multiple times to listen to more than one publisher
        """
        self._socket.connect('tcp://' + host + ':' + str(port))

    def listen(self):
        """ Listens for heartbeat messages

        Returns the name of the sender of the heartbeat
        """
        if self._socket.poll(self._timeout) != 0:
            return self._socket.recv_string()
        return ''

    def destroy(self):
        self._contex.destroy()
