# -*- coding: utf-8 -*-
"""Processing Controller Scheduler.

This provides the Scheduler event loop, implemented using a set of
asynchronous coroutines which provide the following functionality

1. Watch for new Scheduling and Processing Block events (in the Configuration
   database)
2. Print the contents of the Processing queue.
3. Schedule Processing Blocks for Execution
4. Update Processing Block status in the Configuration database.

This is backed by an in memory store of Processing Blocks
"""
import asyncio
import functools
import os
import random
import signal
import logging
import json

from .db import get_processing_block, \
                get_processing_block_event, \
                get_scheduling_block, \
                get_scheduling_block_event, \
                get_scheduling_block_ids
from mock_processing_block_controller.tasks import execute_processing_block
from .queue import ProcessingBlockQueue


LOG = logging.getLogger('sip.processing_block_scheduler')


class ProcessingBlockScheduler:
    """Processing Block Scheduler class."""

    def __init__(self, report_rate=5.0):
        """Initialise the Processing bock Scheduler.

        Args:
            report_rate (float): Minimum interval to report the queue status,
                                 in seconds.
        """
        self._queue = ProcessingBlockQueue()
        self._report_rate = report_rate

    def run(self):
        """Starts the Scheduler event loop."""
        loop = asyncio.get_event_loop()
        LOG.info('Starting Processing Block Controller Scheduler, pid = %s.',
                 os.getpid())
        LOG.info('Send SIGINT (Ctrl-C) or SIGTERM to exit.')
        self._init()
        asyncio.ensure_future(self._watch_scheduling_blocks_events())
        asyncio.ensure_future(self._watch_processing_block_events())
        asyncio.ensure_future(self._schedule_processing_block())
        asyncio.ensure_future(self._update_processing_block_status())
        asyncio.ensure_future(self._report_queue_status())
        asyncio.ensure_future(self._report_processing_block_controller_status())
        for sig_name in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, sig_name),
                                    functools.partial(self._ask_exit, sig_name))
        try:
            loop.run_forever()
        finally:
            loop.close()

    def _init(self):
        """"Initialise the queue from the configuration database"""
        block_ids = get_scheduling_block_ids()
        for block_id in block_ids:
            scheduling_block = get_scheduling_block(block_id)
            for processing_block in scheduling_block.get('processing_blocks'):
                processing_block['scheduling_block_id'] = block_id
                priority = random.randint(0, 5)
                # TODO(BM) Check status of blocks before adding them to the
                # queue - Need to check they have not already executed etc.
                # this can be done by checking their status
                # TODO(BM) should also look for running Celery tasks here
                # an check against the Configuration db.
                self._queue.put(processing_block.get('id'), priority=priority)
        LOG.info('Initialised Processing Queue, %d Processing Blocks '
                 'registered.',len(self._queue))

    def _ask_exit(self, sig_name):
        LOG.info('Signal %s received, cancelling tasks ...' % sig_name)
        for task in asyncio.Task.all_tasks():
            # print('---', task, task.cancel())
            task.cancel()
        asyncio.ensure_future(self._exit())

    @staticmethod
    async def _exit():
        loop = asyncio.get_event_loop()
        loop.stop()
        LOG.info('Event loop stopped!')

    async def _watch_scheduling_blocks_events(self):
        """Function to watch for scheduling block events."""
        LOG.info('Starting watch for Scheduling Block events')
        while True:
            try:
                event = get_scheduling_block_event()
                if event:
                    if event['type'] == 'created':
                        await self._register_scheduling_block(event['id'])
                    elif event['type'] == 'deleted':  # == cancelled
                        await self._remove_scheduling_block(event['id'])
                    else:
                        LOG.info('ERROR: Unknown event type!')
                await asyncio.sleep(0.25)  # Release control for >= VALUE
            except asyncio.CancelledError:
                LOG.info('Cancelling watching for Scheduling Block events')
                break

    async def _register_scheduling_block(self, block_id):
        """Register a Scheduling Block with the Scheduler.

        This involves extracting Processing Blocks and removing them from the
        Scheduler queue.

        Args:
            block_id (str): Scheduling block id.
        """
        LOG.info("Registering Scheduling Block: %s" % block_id)
        config = get_scheduling_block(block_id)
        processing_blocks = config.get('processing_blocks')
        if not processing_blocks:
            return
        for processing_block in processing_blocks:
            priority = random.randint(0, 5)
            block_id = processing_block.get('id')
            try:
                self._queue.put(block_id, priority)
            except KeyError:
                return
        LOG.info('Added %d processing blocks to the queue',
                 len(processing_blocks))

    async def _remove_scheduling_block(self, block_id):
        """Remove a Scheduling Block from the queue.

        Args:
            block_id (str): Scheduling Block id
        """
        LOG.info("Removing Scheduling Block: %s ...", block_id)
        indexes = [i for i in range(len(self._queue))
                   if self._queue[i][2].startswith(block_id)]
        block_ids = [self._queue[i][2] for i in indexes]
        for i in range(len(block_ids)):
            LOG.info("Removing Processing Block %03d: id = %s", indexes[i],
                     block_ids[i])
            # TODO(BM) Cancel Celery tasks
            self._queue.remove(block_ids[i])

    async def _watch_processing_block_events(self):
        """Function to watch for processing (delete) block events"""
        LOG.info('Starting watch for Processing Block events')
        while True:
            try:
                event = get_processing_block_event()
                if event:
                    if event['type'] == 'deleted':
                        await self._remove_processing_block(event['id'])
                    else:
                        LOG.info('ERROR: Unknown event type!')
                await asyncio.sleep(0.25)
            except asyncio.CancelledError:
                LOG.info('Cancelling watching for Processing Block events')
                break

    async def _remove_processing_block(self, block_id):
        """Remove a processing block from the queue"""
        try:
            self._queue.remove(block_id)
            LOG.info("Removed Processing Block: %s", block_id)
            # TODO(BM) Cancel Celery task
        except KeyError:
            return

    async def _schedule_processing_block(self):
        """Function to schedule a Processing block for execution."""
        LOG.info('Starting to schedule Processing Block execution')
        while True:
            try:
                # TODO(BM): check SDP state to determine if this should proceed.
                # Look at the highest priority block in the queue
                if len(self._queue) > 0:
                    item = self._queue[0]
                    block_id = item[2]
                    # print('Considering Block:', block_id)
                    # TODO(BM) Check resource availability
                    # TODO(BM) Provision resources
                    # TODO(BM) Check resources are provisioned
                    if await self._check_block_resources(block_id):
                        processing_block = self._queue.get()
                        # TODO(BM) Mark the status of the block as started
                        # executing
                        LOG.info('Executing block %s', processing_block[2])
                        block_config = get_processing_block(block_id)
                        LOG.debug('Block Config: %s', json.dumps(block_config))
                        execute_processing_block.apply_async((block_config,))
                await asyncio.sleep(0.25)  # Release control for >= VALUE
            except asyncio.CancelledError:
                LOG.info('Cancelling scheduling of Processing Block execution')
                break

    @staticmethod
    async def _check_block_resources(block_id):
        """Return True if resources are ready for the specified block.

        Args:
            block_id (str): Processing block id
        """
        value = random.randint(0, 20)
        return value >= 19

    async def _update_processing_block_status(self):
        """Updates the status of executing processing blocks."""
        # TODO(BM) Find out which celery tasks are currently executing
        # TODO(BM) update status of executing tasks in the configuration db.
        LOG.info('Starting update of Processing Block status')
        while True:
            try:
                await asyncio.sleep(0.25)
            except asyncio.CancelledError:
                LOG.info('Cancelling update of Processing Block status')
                break

    async def _report_queue_status(self):
        """Print the contents of the queue."""
        LOG.info('Starting reporting on Processing Block queue')
        while True:
            try:
                if len(self._queue) > 0:
                    LOG.info("Processing Blocks: (index | priority | block_id)")
                    LOG.info('-' * 60)
                    LOG.info(self._queue)
                    LOG.info('-' * 60)
                else:
                    LOG.info("Processing Block queue empty!")
                await asyncio.sleep(self._report_rate)
            except asyncio.CancelledError:
                LOG.info('Cancelling reporting on Processing Block queue')
                break

    async def _report_processing_block_controller_status(self):
        """Print the status of Processing Block Controllers."""
        LOG.info('Starting reporting on Processing Block Controllers')
        while True:
            try:
                await asyncio.sleep(self._report_rate)
            except asyncio.CancelledError:
                LOG.info('Cancelling reporting on Processing Block '
                         'Controllers')
                break
