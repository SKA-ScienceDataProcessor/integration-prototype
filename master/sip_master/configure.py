# coding: utf-8
"""A thread class run when the master controller is configured."""

__author__ = 'David Terrett'

import threading

from sip_common.logging_api import log
from sip_master import config
from sip_master import slave_control


class Configure(threading.Thread):
    """Does the actual work of configuring the system."""

    def __init__(self):
        super(Configure, self).__init__()

    def run(self):
        """Thread run routine."""

        log.info('Starting configuration.')

        # Go through the slave map and start all the tasks that are marked
        # as being required for the system to be online. For these tasks
        # we use the same string for both the task name and type as, by
        # definition there is only one task of each type.
        for task, cfg in config.slave_config.items():
            if cfg.get('online', False):
                slave_control.start(task, task)

        log.info('Configuration thread exiting.')
