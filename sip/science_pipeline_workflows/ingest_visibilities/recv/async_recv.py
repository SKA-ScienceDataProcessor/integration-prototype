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
import sys

import spead2
import spead2.recv
import spead2.recv.asyncio


class SpeadReceiver(object):
    """Receives visibility data using SPEAD."""
    def __init__(self, spead_config):
        self._config = spead_config
        self._streams = []
        self._item_group = spead2.ItemGroup()
        self._num_buffers = self._config['num_buffers']
        self._num_buffer_times = self._config['num_buffer_times']
        self._num_streams = self._config['num_streams']

        # Create the streams.
        port_start = self._config['port_start']
        for i_stream in range(self._num_streams):
            stream = spead2.recv.asyncio.Stream(
                spead2.ThreadPool(), max_heaps=1, contiguous_only=False)
            pool = spead2.MemoryPool(
                self._config['memory_pool']['lower'],
                self._config['memory_pool']['upper'],
                self._config['memory_pool']['max_free'],
                self._config['memory_pool']['initial'])
            stream.set_memory_allocator(pool)
            stream.add_udp_reader(port_start + i_stream)
            self._streams.append(stream)

    def process_buffer(self, i_block, receive_buffer):
        """Blocking function to process the received heaps.
        This is run from an executor.
        """
        logging.info("Worker thread processing block %i", i_block)
        for heap in receive_buffer.result():
            if isinstance(heap, spead2.recv.Heap):
                items = self._item_group.update(heap)
                if 'correlator_output_data' in items:
                    num_baselines = items['correlator_output_data'] \
                        .value.shape[0]
                    val = int(items['correlator_output_data']
                              .value['VIS'][0][0].real)
                    # pylint: disable=logging-format-interpolation
                    logging.info("Data: {}, Length: {}".format(
                        items['correlator_output_data'].value[0],
                        num_baselines))
                    if (val >= i_block * self._config['num_buffer_times'] +
                            self._config['num_buffer_times']):
                        raise RuntimeError('Got time index %i - this '
                                           'should never happen!' % val)
            else:
                logging.info("Dropped incomplete heap %i!", heap.cnt + 1)

    async def _run_loop(self, executor):
        """Main loop."""
        loop = asyncio.get_event_loop()

        # Get first heap in each stream (should be empty).
        for stream in self._streams:
            await stream.get(loop=loop)

        i_block = 0
        receive_buffer = [None, None]
        while True:
            logging.info("Receiving block %i", i_block)

            # Process the previous buffer, if available.
            processing_tasks = None
            if i_block > 0:
                i_buffer_proc = (i_block - 1) % 2
                processing_tasks = loop.run_in_executor(
                    executor, self.process_buffer, i_block - 1,
                    receive_buffer[i_buffer_proc])

            # Set up asynchronous receive on all streams.
            i_buffer_recv = i_block % 2
            receive_tasks = []
            for stream in self._streams:
                for _ in range(self._num_buffer_times):
                    # NOTE: loop.create_task() is needed to schedule these
                    # in the right order!
                    receive_tasks.append(
                        loop.create_task(stream.get(loop=loop)))
            receive_buffer[i_buffer_recv] = asyncio.gather(*receive_tasks)

            # Ensure asynchronous receives and previous processing tasks are
            # done.
            await receive_buffer[i_buffer_recv]
            if processing_tasks:
                await processing_tasks

            logging.info("Received block %i", i_block)
            i_block += 1

    def run(self):
        """Starts the receiver."""
        # Create the thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1)

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
        raise RuntimeError('Usage: python3 async_recv.py <json config>')

    # Set up logging.
    logging.basicConfig(format='%(asctime)-15s %(name)s %(threadName)-22s'
                               ' %(message)s',
                        level=logging.INFO)

    # Load SPEAD configuration from JSON file.
    # with open(sys.argv[-1]) as f:
    #     spead_config = json.load(f)
    spead_config = json.loads(sys.argv[1])

    # Set up the SPEAD receiver and run it (see method, above).
    receiver = SpeadReceiver(spead_config)
    receiver.run()


if __name__ == '__main__':
    main()
