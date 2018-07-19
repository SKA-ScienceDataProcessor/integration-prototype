# coding=utf-8
"""Processing Block Scheduler.

Implemented with a set of long running threads.
"""
import logging
import time
from threading import Thread, Lock
import sys

from .db.client import ConfigDb
from .queue import ProcessingBlockQueue

LOG = logging.getLogger('sip.ec.pc_scheduler')


class ProcessingBlockScheduler:
    """Processing Block Scheduler class."""

    def __init__(self, report_interval=2.0):
        """Initialise the Scheduler.

        Args:
            report_interval (float): Minimum interval between reports, in s

        """
        self._db = ConfigDb()
        self._queue = ProcessingBlockQueue()
        self._report_interval = report_interval
        self._value = ''
        self._value_lock = Lock()

    def _update_value(self, new_value):
        """Update the value."""
        self._value_lock.acquire()
        self._value = new_value
        self._value_lock.release()

    def _monitor_events(self):
        """Watch for Processing Block events."""
        LOG.info('Starting Processing Block event monitor.')
        while True:
            event = self._db.get_latest_event('')
            # if event:
            #     LOG.debug('Acknowledged event of type %s', event['type'])
            LOG.debug('Checking for new events ... %s', self._value)
            self._update_value('a')
            time.sleep(0.2)

    def _report_queue(self):
        """Report on the status of the Processing Block queue(s)
        """
        LOG.info('Starting Processing Block queue reporter.')
        while True:
            LOG.info('Queue status ... %s', self._value)
            self._update_value('b')
            time.sleep(self._report_interval)

    def start(self):
        """Start the Scheduler."""
        scheduler_threads = [
            Thread(target=self._report_queue, daemon=True),
            Thread(target=self._monitor_events, daemon=True)
        ]

        for thread in scheduler_threads:
            thread.start()

        try:
            for thread in scheduler_threads:
                thread.join()
        except KeyboardInterrupt:
            LOG.info('INTERRUPT')
            sys.exit(0)
        finally:
            LOG.info('FINALLY!')

