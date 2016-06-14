""" Heartbeat listener

A HeartbeatListener runs in a separate thread and once a second looks for
heartbeat messages sent by slave controllers. If a message is received from
a slave, that slave's timeout counter is reset. The counter for all the other
slaves is decremented and if any have reached zero the slave is marked as
timed-out in the global slave map and an error message logged.
"""
__author__ = 'David Terrett'

import rpyc
import threading

from sip_common import heartbeat
from sip_common import logger

from sip_master.slave_map import slave_map
from sip_master import config

class HeartbeatListener(threading.Thread):
    def __init__(self, sm):
        """ Creates a heartbeat listener with a 1s timeout
        """
        self._listener = heartbeat.Listener(1000)
        super(HeartbeatListener, self).__init__(daemon=True)

    def connect(self, host, port):
        """ Connect to a sender
        """
        self._listener.connect(host, port)

    def run(self):
        """ Listens for heartbeats and updates the slave map

        Each time round the loop we decrement all the timeout counter for all
        the running slaves then reset the count for any slaves that we get
        a message from. If any slaves then have a count of zero we log a
        message and change the state to 'timed out'.
        """
        global slave_map
        while True:

            # Decrement timeout counters
            for slave in slave_map:
                if slave_map[slave]['state'] == 'running':
                    slave_map[slave]['timeout counter'] -= 1

            # Process any waiting messages
            msg = self._listener.listen()
            while msg != '':
                name = msg[0]
                state = msg[1]

                # Reset counters of slaves that we get a message from
                slave_map[name]['timeout counter'] = (
                       slave_map[name]['timeout'])

                # Store the state from the message
                slave_map[name]['new_state'] = state

                # Check for more messages
                msg = self._listener.listen()

            # Check for timed out slaves
            for slave in slave_map:
                if slave_map[slave]['state'] == 'loaded' and (
                         slave_map[slave]['timeout counter'] == 0):
                    slave_map[slave]['new_state'] = 'timed out'
                    logger.error('No heartbeat from slave controller "' + 
                                 slave + '"')

                # Process slave state change
                if slave_map[slave]['new_state'] != slave_map[slave]['state']:
                     self._update_slave_state(slave, slave_map[slave])

            # Evalute the state of the system
            new_state = self._evaluate_state()

            # If the state has changed, post the appropriate event
            old_state = config.state_machine.current_state()
            if old_state == 'configuring' and new_state == 'available':
                config.state_machine.post_event(['configure done'])
            if old_state == 'available' and new_state == 'degraded':
                config.state_machine.post_event(['degrade'])
            if old_state == 'available' and new_state == 'unavailable':
                config.state_machine.post_event(['degrade'])
            if old_state == 'degraded' and new_state == 'unavailable':
                config.state_machine.post_event(['degrade'])
            if old_state == 'unavailable' and new_state == 'degraded':
                config.state_machine.post_event(['upgrade'])
            if old_state == 'unavailable' and new_state == 'available':
                config.state_machine.post_event(['upgrade'])
            if old_state == 'degraded' and new_state == 'available':
                config.state_machine.post_event(['upgrade'])

    def _evaluate_state(self):
        """ Evaluate current status

        This examines the states of all the slaves and decides what state
        we are in.

        For the moment it just looks to see if the LTS is loaded
        """
        if slave_map['LTS']['state'] == 'loaded':
            return 'available'
        else:
            return 'unavailable'

    def _update_slave_state(self, name, rec):
        old_state = rec['state']
        rec['state'] = rec['new_state']

        # If the state went from 'starting' to 'running' send a
        # load command to the slave.
        if old_state == 'starting' and rec['state'] == 'running':
            conn = rpyc.connect(rec['address'], rec['rpc_port'])
            conn.root.load()
            rec['state']= 'loading'

