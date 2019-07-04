# coding=utf-8
"""Processing Block Scheduler.

Implemented with a set of long running threads.
"""
import datetime
import os
import sys
import time
from threading import Thread, active_count

import celery
from celery.app.control import Inspect

from sip_config_db.scheduling import ProcessingBlock, ProcessingBlockList
from sip_config_db.utils.datetime_utils import datetime_from_isoformat
from .log import LOG
from .pb_queue import ProcessingBlockQueue
from .release import __service_name__


BROKER = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
APP = celery.Celery(broker=BROKER, backend=BACKEND)


execution_task_name = 'sip_pbc.tasks.execute_processing_block'

class ProcessingBlockScheduler:
    # pylint: disable=too-few-public-methods
    """Processing Block Scheduler class."""

    def __init__(self, report_interval: float = 5.0, max_pbcs: int = 4):
        """Initialise the Scheduler.

        Args:
            report_interval (float): Minimum interval between reports, in s
            max_pbcs (int): Maximum number of concurrent PBCs
                (and therefore PBs) that can be running.

        """
        LOG.info('Starting Processing Block Scheduler.')
        self._queue = self._init_queue()
        self._pb_events = ProcessingBlockList().subscribe(__service_name__)
        self._report_interval = report_interval
        self._num_pbcs = 0  # Current number of PBCs
        self._max_pbcs = max_pbcs
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

    def _monitor_events(self):
        """Watch for Processing Block events."""
        LOG.info("Starting to monitor PB events")
        check_counter = 0
        while True:
            if check_counter == 50:
                check_counter = 0
                LOG.debug('Checking for PB events...')

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
                        LOG.info('Acknowledged PB completed event (%s) for %s,'
                                 ' [timestamp: %s]', event.id,
                                 event.object_id, event.timestamp)
                        self._num_pbcs -= 1
                        if self._num_pbcs < 0:
                            self._num_pbcs = 0

            time.sleep(0.1)
            check_counter += 1

    def _processing_controller_status(self):
        """Report on the status of the Processing Block queue(s)."""
        LOG.info('Starting Processing Block queue reporter.')
        while True:
            LOG.info('PB queue length = %d', len(self._queue))
            time.sleep(self._report_interval)
            if active_count() != 5:
                LOG.critical('Processing Controller not running '
                             'correctly! (%d/%d threads active)',
                             active_count(), 5)

    def _schedule_processing_blocks(self):
        """Schedule Processing Blocks for execution."""
        LOG.info('Starting to Schedule Processing Blocks.')
        while True:
            time.sleep(0.5)
            if not self._queue:
                continue
            if self._num_pbcs >= self._max_pbcs:
                LOG.warning('Resource limit reached!')
                continue
            _inspect = Inspect(app=APP)
            if self._queue and _inspect.active() is not None:
                next_pb = self._queue[-1]
                LOG.info('Considering %s for execution...', next_pb[2])
                utc_now = datetime.datetime.utcnow()
                time_in_queue = (utc_now -
                                 datetime_from_isoformat(next_pb[4]))
                if time_in_queue.total_seconds() >= 10:
                    item = self._queue.get()
                    LOG.info('------------------------------------')
                    LOG.info('>>> Executing %s! <<<', item)
                    LOG.info('------------------------------------')
                    APP.send_task(execution_task_name, args=(item,))
                    self._num_pbcs += 1
                else:
                    LOG.info('Waiting for resources for %s', next_pb[2])

    def _monitor_pbc_status(self):
        """Monitor the PBC status."""
        LOG.info('Starting to Monitor PBC status.')
        inspect = APP.control.inspect()
        workers = inspect.ping()
        start_time = time.time()
        while workers is None:
            time.sleep(0.1)
            elapsed = time.time() - start_time
            if elapsed > 20.0:
                LOG.warning('PBC not found!')
                break
        if workers is not None:
            for worker in workers:
                _tasks = inspect.registered_tasks()[worker]
                LOG.info('Worker: %s tasks:', worker)
                for task_index, task_name in enumerate(_tasks):
                    LOG.info('  %02d : %s', task_index, task_name)

        while True:
            LOG.info('Checking PBC status (%d/%d)', self._num_pbcs,
                     self._max_pbcs)
            inspect = APP.control.inspect()
            workers = inspect.ping()
            if workers is None:
                LOG.warning('PBC service not found!')
            else:
                LOG.info('PBC state:  %s', APP.events.State())
                _active = inspect.active()
                _scheduled = inspect.scheduled()
                for worker in workers:
                    LOG.info('  Worker %s: scheduled: %s, active: %s',
                             worker, _active[worker], _scheduled[worker])
            time.sleep(self._report_interval)

    def start(self):
        """Start the scheduler threads."""
        # TODO(BMo) having this check is probably a good idea but I've \
        # disabled it for now while the PBC is in flux.
        # assert sip_pbc.release.__version__ == '1.2.3'

        scheduler_threads = [
            Thread(target=self._monitor_events, daemon=True),
            Thread(target=self._processing_controller_status, daemon=True),
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
