# -*- coding: utf-8 -*-
"""Receives visibility data asynchronously using SPEAD.

Usage: python3 async_recv.py <spead_recv.json>

The command line arguments are:
    - spead_recv.json:              Path to a JSON file containing
                                    the SPEAD configuration. See below.
"""
import asyncio
import concurrent.futures
import json
import logging
import math
import queue
import threading
import sys
import time

import numpy
import spead2
import spead2.recv
import spead2.recv.asyncio


class SpeadReceiver(object):
    """Receives visibility data using SPEAD."""
    def __init__(self, spead_config):
        self._config = spead_config
        self._buffer = []
        self._streams = []
        self._num_buffers = self._config['num_buffers']
        self._num_buffer_times = self._config['num_buffer_times']
        self._num_streams = self._config['num_streams']
        self.q = queue.Queue(self._num_buffers)

        # Create the buffers.
        # self.buffer is a list of dictionaries.
        # Each dictionary contains a reference to an array of visibility data,
        # and an array to keep track of the number of free time slots
        # in the buffer for each channel.
        # When the total number of free slots in the buffer reaches zero,
        # it is ready for processing.
        # Each buffer also contains a flag to keep track of whether
        # it has been queued for processing.
        for _ in range(self._num_buffers):
            counters = numpy.ones((self._num_streams,), 'i4') * \
                    self._num_buffer_times
            self._buffer.append(
                {'vis_data': None, 'counters': counters, 'queued': False})

        # Create the streams.
        port_start = self._config['port_start']
        for i_stream in range(self._num_streams):
            stream = spead2.recv.asyncio.Stream(
                spead2.ThreadPool(), contiguous_only=False)
            pool = spead2.MemoryPool(
                self._config['memory_pool']['lower'],
                self._config['memory_pool']['upper'],
                self._config['memory_pool']['max_free'],
                self._config['memory_pool']['initial'])
            stream.set_memory_allocator(pool)
            stream.add_udp_reader(port_start + i_stream)
            self._streams.append((stream, spead2.ItemGroup()))

    async def _run_loop(self, executor):
        """Main loop."""
        loop = asyncio.get_event_loop()

        # Get first heap in each stream (should be empty).
        for stream, item_group in self._streams:
            heap = await stream.get(loop=loop)
            item_group.update(heap)

        i_block = 0
        while True:
            logging.info("Receiving block %i", i_block)
            # Launch asynchronous receive on all streams.
            i_buffer = i_block % self._num_buffers
            receive_tasks = []
            for (stream, _) in self._streams:
                for i_time in range(self._num_buffer_times):
                    # NOTE: loop.create_task() is needed to schedule these
                    # in the right order!
                    receive_tasks.append(
                        loop.create_task(stream.get(loop=loop)))
            receive_results = asyncio.gather(*receive_tasks)
            await receive_results

            i = 0
            for i_stream, (_, item_group) in enumerate(self._streams):
                for i_time in range(self._num_buffer_times):
                    heap = receive_results.result()[i]
                    if isinstance(heap, spead2.recv.Heap):
                        items = item_group.update(heap)
                        if 'correlator_output_data' in items:
                            num_baselines = items['correlator_output_data'].value.shape[0]
                            logging.info("Data: {}, Length: {}".format(
                                items['correlator_output_data'].value[0],
                                num_baselines))
                            expected = i_time + i_block * self._num_buffer_times + i_stream / 1000.0
                            actual = items['correlator_output_data'].value['VIS'][0][0].real
                            if abs(actual - expected) > 1e-5:
                                msg = ">>>>>>>>>>>>>>>>>>>>>>>>> Argh! Expected %.3f, got %.3f" % (expected, actual)
                                logging.warning(msg)
                                # raise RuntimeError(msg)
                    else:
                        logging.info("Dropped incomplete heap %i on channel %i!", heap.cnt + 1, i_stream)
                    i += 1

            logging.info("Received block %i", i_block)
            i_block += 1

    def run(self):
        """Starts the receiver."""
        # Create the thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._config['num_workers'])

        # Run the event loop.
        loop = asyncio.get_event_loop()
        try:
            # Asynchronously receive and process data on all channels.
            loop.run_until_complete(self._run_loop(executor))
        except KeyboardInterrupt:
            pass
        finally:
            # Shut down.
            logging.info('Shutting down...')
            executor.shutdown()
            # loop.close()  # Not required.


def main():
    """Main function for SPEAD receiver module."""
    # Check command line arguments.
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: python3 async_recv.py <spead_recv.json>')

    # Set up logging.
    logging.basicConfig(format='%(asctime)-15s %(threadName)-12s %(levelname)-10s %(message)s',
                        level=logging.INFO)

    # Load SPEAD configuration from JSON file.
    with open(sys.argv[-1]) as f:
        spead_config = json.load(f)

    # Set up the SPEAD receiver and run it (see method, above).
    receiver = SpeadReceiver(spead_config)
    receiver.run()


if __name__ == '__main__':
    main()
