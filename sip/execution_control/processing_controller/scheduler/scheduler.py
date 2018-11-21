# coding=utf-8
"""Processing Block Scheduler.

Implemented with a set of long running threads.
"""
import logging
import time
from threading import Thread, Lock
import sys

# from .db.scheduling_data import ConfigDb
from .pb_queue import ProcessingBlockQueue
from sip_config_db.scheduling import ProcessingBlockList
from processing_block_controller.tasks import execute_processing_block
from .log import LOG
from .release import __service_name__



class ProcessingBlockScheduler:
    # pylint: disable=too-few-public-methods
    """Processing Block Scheduler class."""

    def __init__(self, report_interval=2.0):
        """Initialise the Scheduler.

        Args:
            report_interval (float): Minimum interval between reports, in s

        """
        LOG.info('Starting Processing Block Scheduler.')
        # self._db = ConfigDb()
        self._queue = self._init_queue()
        self._pb_events = ProcessingBlockList().subscribe(__service_name__)
        self._report_interval = report_interval
        self._value = ''
        self._value_lock = Lock()

    @staticmethod
    def _init_queue():
        """Initialise the Processing Block queue from the database.

        This method should populate the queue from the current state of the
        Configuration Database.

        This needs to be based on the current set of Processing Blocks in
        the database and consider events on these processing blocks.
        """
        LOG.info('Initialising Processing Block queue.')
        queue = ProcessingBlockQueue()
        # TODO(BM) populate queue from the database
        return queue

    def queue(self):
        """Return the processing block queue."""

        print(self._queue)
        return self._queue

    def _update_value(self, new_value):
        """Update the value."""
        self._value_lock.acquire()
        self._value = new_value
        self._value_lock.release()

    def _monitor_events(self):
        """Watch for Processing Block events."""
        LOG.info('Starting Processing Block event monitor.')
        while True:
            # LOG.debug('Checking for new events ... %s', self._value)
            LOG.debug('Checking for new events ...')
            events = self._pb_events.get_published_events()
            if events:
                for event in events:
                    LOG.debug('PB event type=%s, pb=%s', event.type,
                              event.object_id)
                    execute_processing_block.delay(event.object_id)
            # self._update_value('a')
            time.sleep(0.5)

    def _report_queue(self):
        """Report on the status of the Processing Block queue(s)."""
        LOG.info('Starting Processing Block queue reporter.')
        while True:
            LOG.info('Queue status ... %s', self._value)
            self._update_value('b')
            time.sleep(self._report_interval)

    def _schedule_processing_blocks(self):
        """."""
        LOG.info('Starting to Schedule Processing Blocks.')
        # 1. Check resource availability
        # 2. Determine what next to run on the queue
        # 3. Get PB configuration
        # 4. Launch the PBC for the PB

        # This is where the PBC started (celery)
        while True:
            LOG.info('')
            # if num_pbc == 0:
            #     execute_processing_block.delay()
            time.sleep(self._report_interval)

    def _monitor_pbc_status(self):
        """."""
        LOG.info('Starting to Monitor PBC status.')
        # Report on the state of PBC's
        # 1. Get list of celery workers
        # 2. Get list of celery tasks (active, etc)
        # 3. Find out the status of celery tasks.
        # 4. Update the database with findings
        while True:
            LOG.info('')
            time.sleep(self._report_interval)

    def start(self):
        """Start the scheduler threads."""
        scheduler_threads = [
            Thread(target=self._monitor_events, daemon=True)
            # Thread(target=self._report_queue, daemon=True),
            # Thread(target=self._schedule_processing_blocks, daemon=True),
            # Thread(target=self._monitor_pbc_status, daemon=True)
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
