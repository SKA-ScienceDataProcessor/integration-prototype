# coding: utf-8
"""Slave poller.

A SlavePoller runs in a separate thread and once a second looks at the
status of all the slave controllers using the Paas service.

The states of states of all the slaves is then checked against a list of
those that need to be running for the system to be considered available,
degraded or unavailable and an appropriate event posted.
"""

__author__ = 'David Terrett'

import copy
import threading
import time

from sip.common.logging_api import log
from sip.common.paas import TaskStatus
from sip.master.config import slave_status_dict
from sip.master.config import slave_config_dict
from sip.master.slave_states import SlaveStatus


class SlavePoller(threading.Thread):
    """This class checks on the state of slaves
    """

    def __init__(self, sm):
        """Constructor.
        """
        self._sm = sm
        super(SlavePoller, self).__init__(daemon = True)

    def run(self):
        """
        """
        log.info('Starting Slave poller.')
        while True:

            # Scan all the tasks in the status dictionary and update
            # the state machines
            for name, status in copy.copy(slave_status_dict()).items():

                # If there is a PAAS descriptor for this task
                if  status['descriptor']:

                    # Get the status from the PAAS. This could fail if
                    # the task was deleted after we copied the status
                    # dictionary
                    state = TaskStatus.UNKNOWN
                    try:
                        state = status['descriptor'].status()

                        # If the state is "running" inquire the slave status
                        # via the slave controller RPC interface.
                        if state == TaskStatus.RUNNING:
                    
                            # Test whether we can connect to the RPC service
                            controller = status['task_controller']
                            try:
                                controller.connect()

                                # Connection is alive so get the slave status
                                state = controller.status()

                                # Convert to state machine event
                                if state == 'idle':
                                    state = SlaveStatus.idle
                                elif state == 'busy':
                                    state = SlaveStatus.busy
                                elif state == 'error':
                                    state = SlaveStatus.error
                            except:

                                # Slave contoller is not listening
                                state = SlaveStatus.noConnection
                    except:
                        pass

                    # Post the event to the slave state machine 
                    status['state'].post_event([state])

            # Evaluate the state of the system
            self._evaluate_state()

            time.sleep(1.0)

    def _evaluate_state(self):
        """Evaluates the current status.

        This examines the states of all the slaves and posts an appropriate
        event.
        """
        # Count the number of services
        number_of_services = 0
        services_running = 0
        for task, config in slave_config_dict().items():
            if config['online']:
                number_of_services += 1
                if task in slave_status_dict() and (
                        slave_status_dict()[task]['state'].\
                        current_state()) == 'Running_busy':
                    services_running += 1

        # Count the number of running tasks
        tasks_running = 0
        for task, status in slave_status_dict().items():
            if slave_status_dict()[task]['state'].current_state() == \
                        'Running_busy':
                tasks_running += 1

        # Post an event to the MC state machine
        if tasks_running == 0:
            self._sm.post_event(['no tasks'])
        if services_running == number_of_services:
            self._sm.post_event(['all services'])
        elif services_running > 0:
            self._sm.post_event(['some services'])
