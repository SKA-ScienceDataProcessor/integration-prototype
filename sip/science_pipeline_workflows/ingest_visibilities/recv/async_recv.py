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
import time

import numpy
import spead2
import spead2.recv
import spead2.recv.asyncio


class SpeadReceiver(object):
    """Receives visibility data using SPEAD."""
    def __init__(self, spead_config):
        self._config = spead_config
        self._log = logging.getLogger('sip.receiver')
        self._streams = []
        self._item_group = spead2.ItemGroup()
        self._num_buffers = self._config['num_buffers']
        self._num_buffer_times = self._config['num_buffer_times']
        self._num_streams = self._config['num_streams']
        self._block = None

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
        This is run in an executor.
        """
        self._log.info("Worker thread processing block %i", i_block)
        time_overall0 = time.time()
        time_unpack = 0.0
        time_write = 0.0
        for i_heap, heap in enumerate(receive_buffer.result()):
            # Skip and log any incomplete heaps.
            if isinstance(heap, spead2.recv.IncompleteHeap):
                self._log.info("Dropped incomplete heap %i", heap.cnt + 1)
                continue

            # Update the item group from this heap.
            items = self._item_group.update(heap)

            # Get the time and channel indices from the heap index.
            i_chan = i_heap // self._num_buffer_times
            i_time = i_heap % self._num_buffer_times

            if 'correlator_output_data' in items:
                vis_data = items['correlator_output_data'].value['VIS']
                if self._block is None:
                    num_baselines = vis_data.shape[0]
                    num_pols = vis_data[0].shape[0]
                    self._block = numpy.zeros((self._num_buffer_times,
                                               self._num_streams,
                                               num_baselines),
                                              dtype=('c8', num_pols))
                    self._block[:, :, :] = 0  # To make the copies faster.

                # Unpack data from the heap into the block to be processed.
                time_unpack0 = time.time()
                self._block[i_time, i_chan, :] = vis_data
                time_unpack += time.time() - time_unpack0

                # Check the data for debugging!
                val = self._block[i_time, i_chan, -1][-1].real
                # self._log.info("Data: %.3f", val)
                if int(val) >= self._num_buffer_times * (i_block + 1):
                    raise RuntimeError('Got time index %i - this '
                                       'should never happen!' % int(val))

        if self._block is not None:
            # Process the buffered data here.
            if self._config['process_data']:
                pass

            # Write the buffered data to storage.
            if self._config['write_data']:
                time_write0 = time.time()
                with open(self._config['filename'], 'ab') as f:
                    # Don't use pickle, it's really slow (even protocol 4)!
                    numpy.save(f, self._block, allow_pickle=False)
                time_write += time.time() - time_write0

        # Report time taken.
        time_overall = time.time() - time_overall0
        self._log.info("Total processing time: %.1f ms", 1000 * time_overall)
        self._log.info("Unpack was %.1f %%", 100 * time_unpack / time_overall)
        self._log.info("Write was %.1f %%", 100 * time_write / time_overall)
        if time_unpack != 0.0:
            self._log.info("Memory speed %.1f MB/s",
                           (self._block.nbytes * 1e-6)  / time_unpack)
        if time_write != 0.0:
            self._log.info("Write speed %.1f MB/s",
                           (self._block.nbytes * 1e-6)  / time_write)

    async def _run_loop(self, executor):
        """Main loop."""
        loop = asyncio.get_event_loop()

        if self._config['filename']:
            with open(self._config['filename'] + '.txt', "w") as text_file:
                text_file.write(
                    "Waiting for %d streams to start..." % self._num_streams)

        # Get first heap in each stream (should be empty).
        self._log.info("Waiting for %d streams to start...", self._num_streams)
        for stream in self._streams:
            await stream.get(loop=loop)

        i_block = 0
        receive_buffer = [None, None]
        while True:
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
            self._log.info("Receiving block %i", i_block)
            try:
                await receive_buffer[i_buffer_recv]
                self._log.info("Received block %i", i_block)
            except spead2.Stopped:
                # Not sure why this exception is never raised!
                self._log.info("Stream Stopped")
                break
            if processing_tasks:
                await processing_tasks

            i_block += 1

    def run(self):
        """Starts the receiver."""
        # Create the thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1)

        # Run the event loop.
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._run_loop(executor))
        except KeyboardInterrupt:
            pass
        finally:
            # Shut down.
            self._log.info('Shutting down...')
            executor.shutdown()
            # loop.close()  # Not required.


def main():
    """Main function for SPEAD receiver module."""
    # Check command line arguments.
    if len(sys.argv) < 2:
        raise RuntimeError('Usage: python3 async_recv.py <json config>')

    # Set up logging.
    logging.basicConfig(format='%(asctime)-23s %(name)-12s %(threadName)-22s '
                               '%(message)s',
                        level=logging.INFO, stream=sys.stdout)

    print(sys.argv[1])

    # Load SPEAD configuration from JSON file.
    # with open(sys.argv[-1]) as f:
    #     spead_config = json.load(f)
    spead_config = json.loads(sys.argv[1])

    # Set up the SPEAD receiver and run it (see method, above).
    receiver = SpeadReceiver(spead_config)
    receiver.run()


if __name__ == '__main__':
    main()
