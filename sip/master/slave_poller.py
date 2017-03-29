# coding: utf-8
"""Slave poller.

A SlavePoller runs in a separate thread and once a second looks at the
status of all the slave controllers using the Paas service.

The states of states of all the slaves is then checked against a list of
those that need to be running for the system to be considered available,
degraded or unavailable and an appropriate event posted.
"""

__author__ = 'David Terrett'

import threading
import time

from sip.common.logging_api import log
from sip.master import config


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
            for name, status in config.slave_status.items():
                if  status['descriptor']:
                    state = status['descriptor'].status()
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
        for task, cfg in config.slave_config.items():
            if cfg.get('online', False):
                number_of_services += 1
                if task in config.slave_status and (
                        config.slave_status[task]['state'].current_state()) == \
                        'Running':
                    services_running += 1

        # Count the number of running tasks
        tasks_running = 0
        for task, status in config.slave_status.items():
            if config.slave_status[task]['state'].current_state() == 'Running':
                tasks_running += 1

        # Post an event to the MC state machine
        if tasks_running == 0:
            self._sm.post_event(['no tasks'])
        if services_running == number_of_services:
            self._sm.post_event(['all services'])
        elif services_running > 0:
            self._sm.post_event(['some services'])
