# coding=utf-8
"""Processing Block Scheduler.

Implemented with a set of long running threads.
"""
import sys
import time
from threading import Lock, Thread

import celery
from celery.app.control import Inspect

from sip_config_db.scheduling import ProcessingBlock, ProcessingBlockList
from .log import LOG
from .pb_queue import ProcessingBlockQueue
from .release import __service_name__
from ..processing_block_controller.tasks import APP, execute_processing_block


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
        self._pb_list = ProcessingBlockList()

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
        active_pb_ids = ProcessingBlockList().active
        for pb_id in active_pb_ids:
            pb = ProcessingBlock(pb_id)
            queue.put(pb.id, pb.priority, pb.type)
        return queue

    def queue(self):
        """Return the processing block queue."""
        LOG.info("Processing Block Queue %s", self._queue)
        # print(self._queue)
        return self._queue

    def _update_value(self, new_value):
        """Update the value."""
        self._value_lock.acquire()
        self._value = new_value
        self._value_lock.release()

    def _monitor_events(self):
        """Watch for Processing Block events."""
        subscriber = 'test_pb_events_subscriber'
        event_queue = self._pb_list.subscribe(subscriber)
        LOG.info('Starting Processing Block event monitor.')
        while True:
            event = event_queue.get()
            if event:
                LOG.debug('Acknowledged event of type %s', event.object_type)
                LOG.debug("Event ID %s", event.id)
                LOG.debug("Event Object ID %s", event.object_id)

                # Adding PB to the queue
                pb = ProcessingBlock(event.object_id)
                self._queue.put(event.object_id, pb.priority, pb.type)

            # LOG.debug('Checking for new events ... %s', self._value)
            # self._update_value('a')
            time.sleep(0.2)

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
        # 1. Check resource availability - Ignoring for now
        # 2. Determine what next to run on the queue
        # 3. Get PB configuration
        # 4. Launch the PBC for the PB

        # This is where the PBC started (celery)
        while True:
            LOG.info('Checking for new Processing blocks to execute')
            while self._queue:
                pb = self._queue.get()
                LOG.info("Processing Block ID: %s", pb[2])
                LOG.info(" PB Priority: %s", pb[0])
                execute_processing_block.delay(pb[2])
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
            LOG.info('Monitoring Processing Block Controller Status')
            task_state = celery.current_app.events.State()
            _inspect = Inspect(app=APP)
            LOG.info('Active: %s', _inspect.active())
            LOG.info('State of the Current Celery Task:  %s',
                     _inspect.stats().keys)
            LOG.info('Celery Workers:  %s', _inspect.stats().keys())
            LOG.info('State of the Current Celery Task:  %s', task_state)
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
