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

import threading
import time

from sip_common import heartbeat, logger
from sip_master import config


class HeartbeatListener(threading.Thread):
    """This class listens to messages from slaves (not tasks).

    Slave messages are sent from 'slave/bin/main'
    The content of the slave message is the slave state global variable.

    This is (currently) set by the _HeartbeatPoller in the slave/task_control.py

    The message sent from the slave must be of the form name:state

    The slave states being sent are allowed to be 'busy' or 'idle'

    a new slave/task_control can be written to handle different messages from
    tasks. The task control used it set in the slave_map.json.
    """

    def __init__(self, sm):
        """ Creates a heartbeat listener that return immediately if there
            are no messages to retrieve.
        """
        self._listener = heartbeat.Listener(0)
        super(HeartbeatListener, self).__init__(daemon=True)

    def connect(self, host, port):
        """Connect to a sender"""
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
                status = config.slave_status[name]

                # Ensure RPyC connection is established
                # once the slave is running
                # (i.e. after the first heartbeat has been received).
                status['task_controller'].connect(status['address'],
                                                  status['rpc_port'])

                # Reset counters of slaves that we get a message from
                status['timeout counter'] = (
                       config.slave_config[status['type']]['timeout'])

                # Post an event according to the state in the heartbeat
                # message
                if state == 'busy':
                    status['state'].post_event(['busy heartbeat'])
                elif state == 'idle':
                    status['state'].post_event(['idle heartbeat'])
                else:
                    logger.error('Invalid state received from slave: {}'.
                                 format(state))

                # Check for more messages.
                msg = self._listener.listen()

            # Check for timed out slaves
            for name, status in config.slave_status.items():
                if status['state'].current_state() != '_End':
                    if status['timeout counter'] == 0:
                        status['state'].post_event(['no heartbeat'])

            # Evaluate the state of the system
            self._evaluate_state()

            time.sleep(1.0)

    def _evaluate_state(self):
        """ Evaluate current status

        This examines the states of all the slaves and posts an event
        """

        # Count the number of services
        number_of_services = 0
        services_running = 0
        for task, cfg in config.slave_config.items():
            if cfg.get('online', False):
                number_of_services += 1
                if task in config.slave_status and (
                        config.slave_status[task]['state'].current_state()) == \
                        'Busy':
                    services_running += 1

        # Count the number of running tasks
        tasks_running = 0
        for task, status in config.slave_status.items():
            if config.slave_status[task]['state'].current_state() == 'Busy':
                tasks_running += 1

        # Post an event to the MC state machine
        if tasks_running == 0:
            config.state_machine.post_event(['no tasks'])
        elif services_running == number_of_services:
            config.state_machine.post_event(['all services'])
        else:
            config.state_machine.post_event(['some services'])
