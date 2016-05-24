""" Heartbeat listener

A HeartbeatListener runs in a separate thread and once a second looks for
heartbeat messages sent by slave controllers. If a message is received from
a slave, that slave's timeout counter is reset. The counter for all the other
slaves is decremented and if any have reached zero the slave is marked as
timed-out in the global slave map and an error message logged.
"""
__author__ = 'David Terrett'

import threading

import heartbeat
import logger

from ._slave_map import _slave_map

class _HeartbeatListener(threading.Thread):
    def __init__(self):

        # Create a heartbeat listener with a 1s timeout
        self._listener = heartbeat.Listener(1000)
        super(_HeartbeatListener, self).__init__(daemon=True)

    def connect(self, endpoint):
        """ Connect to a sender
        """
        self._listener.connect(endpoint)

    def run(self):
        """ Listens for heartbeats and updates the slave map

        Each time round the loop we decrement all the timeout counter for all
        the running slaves then reset the count for any slaves that we get
        a message from. If any slaves then have a count of zero we log a
        message and change the state to 'timed out'.
        """
        global _slave_map
        while True:

            # Decrement timeout counters
            for slave in _slave_map:
                if _slave_map[slave]['state'] == 'running':
                    _slave_map[slave]['timeout counter'] -= 1
            msg = self._listener.listen()

            # Reset counters of slaves that we get a message from
            while msg != '':
                _slave_map[msg]['timeout counter'] = _slave_map[msg]['timeout']
                msg = self._listener.listen()

            # Check for timed out slaves
            for slave in _slave_map:
                if _slave_map[slave]['state'] == 'running' and \
                         _slave_map[slave]['timeout counter'] == 0:
                    _slave_map[slave]['state'] == 'timed out'
                    logger.error('No heartbeat from slave controller "' + 
                                 slave + '"')

# Create and start the global heartbeat listener
global _heartbeat_listener
_heartbeat_listener = _HeartbeatListener()
_heartbeat_listener.start()
