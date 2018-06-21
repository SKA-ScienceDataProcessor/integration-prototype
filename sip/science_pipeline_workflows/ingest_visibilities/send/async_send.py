# -*- coding: utf-8 -*-
"""Sends dummy visibility data asynchronously using SPEAD.

Usage: python3 async_send.py <spead_send.json>

The command line arguments are:
    - spead_send.json:              Path to a JSON file containing
                                    the SPEAD configuration. See below.

An example SPEAD configuration JSON file could be:

    {
        "destination_host": "127.0.0.1",
        "destination_port_start": 41000,
        "heap":
        {
            "num_stations": 512,
            "num_pols": 4
        },
        "num_streams": 10,
        "num_workers": 4,
        "reporting_interval": 10,
        "start_channel": 0,
        "stream_config":
        {
            "max_packet_size": 9172,
            "rate": 20e6,
            "burst_size": 1472,
            "max_heaps": 2
        }
    }

- ``stream_config`` is a dictionary describing the stream configuration.
  See ``https://spead2.readthedocs.io/en/v1.3.2/py-send.html``
"""

import asyncio
import concurrent.futures
import json
import logging
import sys
import time
import os

import numpy
from jsonschema import ValidationError, validate
import spead2
import spead2.send
import spead2.send.asyncio


class SpeadSender(object):
    """Sends dummy visibility data using SPEAD."""
    def __init__(self, spead_config):
        self._config = spead_config
        self._log = logging.getLogger('sip.sender')
        self._streams = []
        self._buffer = []

        # Construct UDP streams and associated item groups.
        stream_config = spead2.send.StreamConfig(
            self._config['stream_config']['max_packet_size'],
            self._config['stream_config']['rate'],
            self._config['stream_config']['burst_size'],
            self._config['stream_config']['max_heaps'])
        for i_stream in range(self._config['num_streams']):
            host = self._config['destination_host']
            port = self._config['destination_port_start'] + i_stream
            # It's much faster to have a thread pool of one thread per stream!
            thread_pool = spead2.ThreadPool(threads=1)
            self._log.info('Creating SPEAD stream on %s:%i ...', host, port)
            udp_stream = spead2.send.asyncio.UdpStream(
                thread_pool, host, port, stream_config)
            # FIXME The ICD specifies SPEAD-64-48 flavour,
            # but this is incompatible with the current set of item IDs.
            item_group = spead2.send.ItemGroup(
                flavour=spead2.Flavour(4, 64, 40, 0))
            self._streams.append((udp_stream, item_group))

    def fill_buffer(self, i_buffer, i_time, i_chan):
        """Blocking function to populate the visibility data array.
        This is run in an executor.
        """
        # Write the data into the buffer.
        self._buffer[i_buffer][i_chan]['VIS'][:] = (i_time + i_chan / 1000.0)

    # pylint: disable=too-many-locals
    async def _run_loop(self, executor):
        """Main loop."""
        # SPEAD heap descriptor.
        # One channel per stream and one time index per heap.
        num_stations = self._config['heap']['num_stations']
        num_pols = self._config['heap']['num_pols']
        num_baselines = num_stations * (num_stations + 1) // 2
        start_chan = self._config['start_channel']
        dtype = [('TCI', 'i1'), ('FD', 'u1'), ('VIS', '<c8', num_pols)]
        descriptor = {
            'visibility_timestamp_count': {
                'id': 0x8000,
                'dtype': '<u4',
            },
            'visibility_timestamp_fraction': {
                'id': 0x8001,
                'dtype': '<u4',
            },
            'visibility_channel_id': {
                'id': 0x8002,
                'dtype': '<u4'
            },
            'visibility_channel_count': {
                'id': 0x8003,
                'dtype': '<u4'
            },
            'visibility_baseline_polarisation_id': {
                'id': 0x8004,
                'dtype': '<u4'
            },
            'visibility_baseline_count': {
                'id': 0x8005,
                'dtype': '<u4'
            },
            'phase_bin_id': {
                'id': 0x8006,
                'dtype': '<u2'
            },
            'phase_bin_count': {
                'id': 0x8007,
                'dtype': '<u2'
            },
            'scan_id': {
                'id': 0x8008,
                'dtype': '<u8'
            },
            'visibility_hardware_id': {
                'id': 0x8009,
                'dtype': '<u4'
            },
            'correlator_output_data': {
                'id': 0x800A,
                'dtype': dtype,
                'shape': (num_baselines,)
            }
        }

        # Create shadow buffers for each stream/channel.
        for i_buffer in range(2):
            self._buffer.append([])
            for _ in range(len(self._streams)):
                self._buffer[i_buffer].append(
                    numpy.zeros((num_baselines,), dtype=dtype))

        # Add items to the item group of each stream.
        for i_stream, (stream, item_group) in enumerate(self._streams):
            for key, item in descriptor.items():
                item_shape = item['shape'] if 'shape' in item else tuple()
                item_group.add_item(
                    id=item['id'], name=key, description='',
                    shape=item_shape, dtype=item['dtype'])

            # Write the header information.
            # Send the start of stream message to each stream.
            item_group['visibility_baseline_count'].value = num_baselines
            item_group['visibility_channel_id'].value = i_stream + start_chan
            await stream.async_send_heap(item_group.get_start())

        # Calculate the total data size being sent.
        num_streams = self._config['num_streams']
        reporting_interval = self._config['reporting_interval']
        data_size = (num_baselines * (num_pols * 8 + 2)) / 1e6
        data_size *= (reporting_interval * num_streams)

        # Enter the main loop over time samples.
        loop = asyncio.get_event_loop()
        i_time = 0
        timer1 = time.time()
        while True:
            # Schedule sends for the previous buffer, if available.
            tasks = []
            if i_time > 0:
                i_buffer = (i_time - 1) % 2
                for i_stream, (stream, item_group) in enumerate(self._streams):
                    item_group['correlator_output_data'].value = \
                        self._buffer[i_buffer][i_stream]
                    tasks.append(stream.async_send_heap(item_group.get_heap()))

            # Fill a buffer by distributing it among worker threads.
            i_buffer = i_time % 2
            for i_stream in range(num_streams):
                tasks.append(loop.run_in_executor(
                    executor, self.fill_buffer, i_buffer, i_time, i_stream))

            # Ensure processing tasks and previous asynchronous sends are done.
            await asyncio.gather(*tasks)

            # Increment time index.
            i_time += 1

            # Periodically report the sender data rate.
            if i_time % reporting_interval == 0:
                self._log.info('Sender data rate (aggregated): %.1f MB/s',
                               data_size / (time.time() - timer1))
                timer1 = time.time()

    def run(self):
        """Starts the sender."""
        # Create the thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._config['num_workers'])

        # Run the event loop.
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._run_loop(executor))
        except KeyboardInterrupt:
            pass
        finally:
            # Send the end of stream message to each stream.
            self._log.info('Shutting down, closing streams...')
            for stream, item_group in self._streams:
                asyncio.wait(stream.async_send_heap(item_group.get_end()))
            self._log.info('... finished.')
            executor.shutdown()
            # loop.close()  # Not required.


def main():
    """Main function for SPEAD sender module."""
    # Check command line arguments.
    if len(sys.argv) != 2:
        raise RuntimeError('Usage: python3 async_send.py <json config>')

    # Set up logging.
    logging.basicConfig(format='%(asctime)-23s %(name)-12s %(threadName)-22s '
                               '%(message)s',
                        level=logging.INFO, stream=sys.stdout)

    # Load SPEAD configuration from JSON file.
    # _path = os.path.dirname(os.path.abspath(__file__))
    # with open(os.path.join(_path, 'spead_send.json')) as file_handle:
    #     spead_config = json.load(file_handle)
    spead_config = json.loads(sys.argv[1])
    try:
        _path = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(_path, 'config_schema.json')
        with open(schema_path) as schema_file:
            schema = json.load(schema_file)
        validate(spead_config, schema)
    except ValidationError as error:
        print(error.cause)
        raise

    # Set up the SPEAD sender and run it (see method, above).
    sender = SpeadSender(spead_config)
    sender.run()


if __name__ == '__main__':
    main()
