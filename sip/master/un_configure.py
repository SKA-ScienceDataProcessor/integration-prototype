# coding: utf-8
"""Functions executed when the master controller is un-configured."""

__author__ = 'David Terrett'

import threading

from sip.common.logging_api import log
from sip.master.config import slave_status_dict


class UnConfigure(threading.Thread):
    """Does the actual work of un-configuring the system.

    Unloads all the loaded tasks
    """
    def __init__(self):
        super(UnConfigure, self).__init__()

    def run(self):
        """Thread run routine."""
        log.info('starting unconfiguration')
        for slave, status in slave_status_dict().items():
            if status['state'].current_state() == 'Running_busy':
                log.info('stopping {}'.format(slave))
                status['task_controller'].stop()
            status['descriptor'].delete()
            status['restart'] = False
        log.info('unconfigure done')
