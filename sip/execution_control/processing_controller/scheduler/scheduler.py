# coding=utf-8
"""Processing Block Scheduler.

Implemented with a set of long running threads.
"""
import datetime
import sys
import time
from threading import Lock, Thread

import celery
from celery.app.control import Inspect

from sip_config_db.scheduling import ProcessingBlock, ProcessingBlockList
from sip_config_db.utils.datetime_utils import datetime_from_isoformat
from .log import LOG
from .pb_queue import ProcessingBlockQueue
from .release import __service_name__
from ..processing_block_controller.tasks import APP, execute_processing_block


class ProcessingBlockScheduler:
    # pylint: disable=too-few-public-methods
    """Processing Block Scheduler class."""

    def __init__(self, report_interval=5.0):
        """Initialise the Scheduler.

        Args:
            report_interval (float): Minimum interval between reports, in s

        """
        LOG.info('Starting Processing Block Scheduler.')
        # LOG.debug('CELERY_BROKER_URL = %s', os.environ['CELERY_BROKER_URL'])
        # LOG.debug('%s', os.environ)
        # self._queue = ProcessingBlockQueue()
        self._queue = self._init_queue()
        self._pb_events = ProcessingBlockList().subscribe(__service_name__)
        self._report_interval = report_interval
        self._num_pbcs = 0  # Current number of PBCs
        self._max_pbcs = 4  # Maximum number of PBCs
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
        LOG.info('Initialising PC PB queue: %s', active_pb_ids)
        for pb_id in active_pb_ids:
            pb = ProcessingBlock(pb_id)
            queue.put(pb.id, pb.priority, pb.type)
        return queue

    def queue(self):
        """Return the processing block queue."""
        return self._queue

    def _update_value(self, new_value):
        """Update the value."""
        self._value_lock.acquire()
        self._value = new_value
        self._value_lock.release()

    def _monitor_events(self):
        """Watch for Processing Block events."""
        LOG.info("Starting to monitor PB events")
        check_counter = 0
        while True:
            if check_counter == 20:
                LOG.debug('Checking for PB events...')
                check_counter = 0
            published_events = self._pb_events.get_published_events()
            for event in published_events:
                if event.type == 'status_changed':
                    LOG.info('PB status changed event: %s',
                             event.data['status'])

                    if event.data['status'] == 'created':
                        LOG.info('Acknowledged PB created event (%s) for %s, '
                                 '[timestamp: %s]', event.id,
                                 event.object_id, event.timestamp)
                        pb = ProcessingBlock(event.object_id)
                        self._queue.put(event.object_id, pb.priority, pb.type)

                    if event.data['status'] == 'completed':
                        LOG.info('Acknowledged PB completed event (%s) for %s, '
                                 '[timestamp: %s]', event.id,
                                 event.object_id, event.timestamp)
                        self._num_pbcs -= 1
                        if self._num_pbcs < 0:
                            self._num_pbcs = 0

            time.sleep(0.1)
            check_counter += 1

    def _report_queue(self):
        """Report on the status of the Processing Block queue(s)."""
        LOG.info('Starting Processing Block queue reporter.')
        while True:
            LOG.info('PB queue length = %d', len(self._queue))
            # LOG.info('Queue status ... %s', self._value)
            # self._update_value('b')
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
            time.sleep(0.5)
            if len(self._queue) == 0:
                continue
            if self._num_pbcs >= self._max_pbcs:
                LOG.warning('Resource limit reached!')
                continue
            _inspect = Inspect(app=APP)
            if len(self._queue) > 0 and _inspect.active() is not None:
                next_pb = self._queue[-1]
                LOG.info('Considering %s for execution...', next_pb[2])
                utc_now = datetime.datetime.utcnow()
                time_in_queue = (utc_now -
                                 datetime_from_isoformat(next_pb[3]))
                if time_in_queue.total_seconds() >= 10:
                    item = self._queue.get()
                    LOG.info('------------------------------------')
                    LOG.info('>>> Executing %s! <<<', item[2])
                    LOG.info('------------------------------------')
                    execute_processing_block.delay(item[2])
                    self._num_pbcs += 1
                else:
                    LOG.info('Waiting for resources for %s', next_pb[2])

    def _monitor_pbc_status(self):
        """."""
        LOG.info('Starting to Monitor PBC status.')
        # Report on the state of PBC's
        # 1. Get list of celery workers
        # 2. Get list of celery tasks (active, etc)
        # 3. Find out the status of celery tasks.
        # 4. Update the database with findings
        while True:
            LOG.info('Checking PBC status (%d/%d)',
                     self._num_pbcs, self._max_pbcs)
            task_state = celery.current_app.events.State()
            _inspect = Inspect(app=APP)
            if _inspect.active() is not None:
                # LOG.info('State of the Current Celery Task:  %s',
                #          _inspect.stats().keys)
                # LOG.info('Celery Workers:  %s', _inspect.stats().keys())
                LOG.info('PBC state:  %s', task_state)
            else:
                LOG.warning('PBC service not found!')
            time.sleep(self._report_interval)

    def start(self):
        """Start the scheduler threads."""
        scheduler_threads = [
            Thread(target=self._monitor_events, daemon=True),
            Thread(target=self._report_queue, daemon=True),
            Thread(target=self._schedule_processing_blocks, daemon=True),
            Thread(target=self._monitor_pbc_status, daemon=True)
        ]

        for thread in scheduler_threads:
            thread.start()

        try:
            for thread in scheduler_threads:
                thread.join()
        except KeyboardInterrupt:
            LOG.info('Keyboard interrupt!')
            sys.exit(0)
        finally:
            LOG.info('Finally!')
