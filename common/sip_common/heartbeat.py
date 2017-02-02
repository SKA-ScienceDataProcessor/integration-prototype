import zmq

"""This defines the SIP API for sending and receiving heartbeat messages."""
__author__ = 'David Terrett'

_context = zmq.Context()
from sip_common.logging_api import log


class Sender:
    """Class for sending heartbeat messages.

        :param name: Name of sender
        :param port: TCP port to bind to
    """
    def __init__(self, name, port=6478):

        # Create a publish socket and bind it to port 6478
        self._socket = _context.socket(zmq.PUB)
        self._socket.bind('tcp://*:' + str(port))

        # Store our name
        self._name = name

    def send(self, status):
        """Send a heartbeat message.

            :param status: status
        """
        self._socket.send_string(self._name + ':' + status)


class Listener:
    """Class for listening for heartbeat messages.

         :param timeout: timeout in milli-seconds
    """
    def __init__(self, timeout):
        self._timeout = timeout

        # Create a subscriber socket that excepts all messages
        self._socket = _context.socket(zmq.SUB)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def connect(self, host, port=6478):
        """Connects to a sender.

        Can be called multiple times to listen to more than one publisher

            :param host: sender host name
            :param port: TCP port to connect to
        """
        try:
            self._socket.connect('tcp://' + host + ':' + str(port))
        except zmq.ZMQError as e:
            log.error(e)

    def listen(self):
        """Listens for heartbeat messages.

        Returns the name of the sender of the heartbeat and the status or
        an empty string if no message is received
        """
        if self._socket.poll(self._timeout) != 0:
            msg = self._socket.recv_string()
            return msg.split(':')
        return ''

