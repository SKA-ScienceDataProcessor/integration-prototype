""" Heartbeat listener

A HeartbeatListener runs in a separate thread and once a second looks for
heartbeat messages sent by slave controllers. If a message is received from
a slave, that slave's timeout counter is reset. The counter for all the other
slaves is decremented and if any have reached zero the slave is marked as
dead in the global slave map and an error message logged.

If a slave state goes from starting to idle it is sent a load command.

The states of states of all the slaves is then checked against a list of
those that need to be running for the system to be considered available,
degraded or unavailable and an appropriate event posted.
"""
__author__ = 'David Terrett'

import rpyc
import threading

from sip_common import heartbeat
from sip_common import logger

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
        message and change the state to 'dead'.
        """
        while True:

            # Decrement timeout counters
            for slave, status in config.slave_status.items():
                if status['timeout counter'] > 0:
                    status['timeout counter'] -= 1

            # Process any waiting messages
            msg = self._listener.listen()
            while msg != '':
                name = msg[0]
                state = msg[1]

                # Reset counters of slaves that we get a message from
                config.slave_status[name]['timeout counter'] = (
                       config.slave_config[name]['timeout'])

                # Store the state from the message
                config.slave_status[name]['new_state'] = state

                # Check for more messages
                msg = self._listener.listen()

            # Check for timed out slaves
            for name, status in config.slave_status.items():
                if status['state'] != '' and (
                         status['timeout counter'] == 0):
                    if status['state'] != 'dead':
                        logger.error('No heartbeat from slave controller "' + 
                                 name + '"')
                    status['new_state'] = 'dead'

                # Process slave state change
                if status['new_state'] != status['state']:
                     self._update_slave_state(name, config.slave_config[slave],
                             status)

            # Evalute the state of the system
            new_state = self._evaluate_state()

            # If the state has changed, post the appropriate event
            old_state = config.state_machine.current_state()
            if old_state == 'Configuring' and new_state == 'Available':
                config.state_machine.post_event(['configure done'])
            if old_state == 'Available' and new_state == 'Degraded':
                config.state_machine.post_event(['degrade'])
            if old_state == 'Available' and new_state == 'Unavailable':
                config.state_machine.post_event(['degrade'])
            if old_state == 'Degraded' and new_state == 'Unavailable':
                config.state_machine.post_event(['degrade'])
            if old_state == 'Unavailable' and new_state == 'Degraded':
                config.state_machine.post_event(['upgrade'])
            if old_state == 'Unavailable' and new_state == 'Available':
                config.state_machine.post_event(['upgrade'])
            if old_state == 'Degraded' and new_state == 'Available':
                config.state_machine.post_event(['upgrade'])

    def _evaluate_state(self):
        """ Evaluate current status

        This examines the states of all the slaves and decides what state
        we are in.

        For the moment it just looks to see if the LTS is loaded
        """
        if config.slave_status['LTS']['state'] == 'busy':
            return 'Available'
        else:
            return 'Unavailable'

    def _update_slave_state(self, name, config, status):
        old_state = status['state']
        status['state'] = status['new_state']

        # If the state went from 'starting' to 'idle' send a
        # load command to the slave.
        if old_state == 'starting' and status['state'] == 'idle':
            conn = rpyc.connect(status['address'], config['rpc_port'])
            conn.root.load(config['task'])
            status['state']= 'loading'

