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
        "max_duration_sec": -1,
        "num_streams": 10,
        "num_workers": 4,
        "reporting_interval_sec": 2,
        "start_channel": 0,
        "stream_config":
        {
            "max_packet_size": 9172,
            "rate": 7.1e6,
            "burst_size": 1472,
            "max_heaps": 2
        }
    }

- ``stream_config`` is a dictionary describing the stream configuration.
  See ``https://spead2.readthedocs.io/en/v1.3.2/py-send.html``
"""

import asyncio
import concurrent.futures
import datetime
import json
import logging
import sys
import time
import os

import numpy
from jsonschema import ValidationError, validate
import sip_logging
import spead2
import spead2.send
import spead2.send.asyncio


class SpeadSender:
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
            item_group = spead2.send.ItemGroup(
                flavour=spead2.Flavour(4, 64, 48, 0))
            self._streams.append((udp_stream, item_group))

    @staticmethod
    def fill_buffer(heap_data, i_chan):
        """Blocking function to populate data in the heap.
        This is run in an executor.
        """
        # Calculate the time count and fraction.
        now = datetime.datetime.utcnow()
        time_full = now.timestamp()
        time_count = int(time_full)
        time_fraction = int((time_full - time_count) * (2**32 - 1))
        diff = now - (now.replace(hour=0, minute=0, second=0, microsecond=0))
        time_data = diff.seconds + 1e-6 * diff.microseconds

        # Write the data into the buffer.
        heap_data['visibility_timestamp_count'] = time_count
        heap_data['visibility_timestamp_fraction'] = time_fraction
        heap_data['correlator_output_data']['VIS'][:][:] = \
            time_data + i_chan * 1j

    # pylint: disable=too-many-locals
    async def _run_loop(self, executor):
        """Main loop."""
        # SPEAD heap descriptor.
        # One channel per stream and one time index per heap.
        max_duration_sec = self._config['max_duration_sec']
        num_stations = self._config['heap']['num_stations']
        num_pols = self._config['heap']['num_pols']
        num_baselines = num_stations * (num_stations + 1) // 2
        reporting_interval_sec = self._config['reporting_interval_sec']
        start_chan = self._config['start_channel']
        dtype = [('TCI', 'i1'), ('FD', 'u1'), ('VIS', '<c8', num_pols)]
        descriptor = {
            'visibility_timestamp_count': {
                'id': 0x6000,
                'dtype': '<u4',
            },
            'visibility_timestamp_fraction': {
                'id': 0x6001,
                'dtype': '<u4',
            },
            'visibility_channel_id': {
                'id': 0x6002,
                'dtype': '<u4'
            },
            'visibility_channel_count': {
                'id': 0x6003,
                'dtype': '<u4'
            },
            'visibility_baseline_polarisation_id': {
                'id': 0x6004,
                'dtype': '<u4'
            },
            'visibility_baseline_count': {
                'id': 0x6005,
                'dtype': '<u4'
            },
            'phase_bin_id': {
                'id': 0x6006,
                'dtype': '<u2'
            },
            'phase_bin_count': {
                'id': 0x6007,
                'dtype': '<u2'
            },
            'scan_id': {
                'id': 0x6008,
                'dtype': '<u8'
            },
            'visibility_hardware_id': {
                'id': 0x6009,
                'dtype': '<u4'
            },
            'correlator_output_data': {
                'id': 0x600A,
                'dtype': dtype,
                'shape': (num_baselines,)
            }
        }

        # Create shadow heap buffers for each stream/channel.
        for i_buffer in range(2):
            self._buffer.append([])
            for _ in range(len(self._streams)):
                heap_data = {
                    'visibility_timestamp_count': 0,
                    'visibility_timestamp_fraction': 0,
                    'correlator_output_data': numpy.zeros(
                        (num_baselines,), dtype=dtype)
                }
                self._buffer[i_buffer].append(heap_data)

        # Add items to each stream's item group, and
        # send the start of stream message to each stream.
        tasks = []
        for i_stream, (stream, item_group) in enumerate(self._streams):
            for key, item in descriptor.items():
                item_shape = item['shape'] if 'shape' in item else tuple()
                item_group.add_item(
                    id=item['id'], name=key, description='',
                    shape=item_shape, dtype=item['dtype'])

            # Write the header information.
            item_group['visibility_channel_id'].value = i_stream + start_chan
            item_group['visibility_channel_count'].value = 1
            item_group['visibility_baseline_count'].value = num_baselines
            tasks.append(stream.async_send_heap(item_group.get_start()))
        await asyncio.gather(*tasks)

        # Calculate the total data size being sent.
        num_streams = self._config['num_streams']
        data_size = (num_baselines * (num_pols * 8 + 2)) / 1e6
        self._log.info('Heap size is %.3f MB', data_size)

        # Enter the main loop over time samples.
        done = False
        loop = asyncio.get_event_loop()
        heaps_sent = 0
        i_time = 0
        start_time = time.time()
        timer1 = time.time()
        while not done:
            # Schedule sends for the previous buffer, if available.
            tasks = []
            if i_time > 0:
                i_buffer = (i_time - 1) % 2
                for i_stream, (stream, item_group) in enumerate(self._streams):
                    for key, value in self._buffer[i_buffer][i_stream].items():
                        item_group[key].value = value  # Update values in heap.
                    # Always send the descriptors AND the static data!
                    tasks.append(stream.async_send_heap(
                        item_group.get_heap(descriptors='all', data='all')))
                    heaps_sent += 1

            # Fill a buffer by distributing it among worker threads.
            i_buffer = i_time % 2
            for i_stream in range(num_streams):
                tasks.append(loop.run_in_executor(
                    executor, self.fill_buffer,
                    self._buffer[i_buffer][i_stream], i_stream))

            # Ensure processing tasks and previous asynchronous sends are done.
            await asyncio.gather(*tasks)

            # Increment time index.
            i_time += 1

            # Periodically report the sender data rate.
            now = time.time()
            if (now - timer1) >= reporting_interval_sec:
                self._log.info('Sent %i heaps in %.3f sec (%.1f MB/s)',
                               heaps_sent, (now - timer1),
                               (data_size * heaps_sent) / (now - timer1))
                heaps_sent = 0
                timer1 = now

            # Check for completion.
            if now - start_time > max_duration_sec > 0:
                done = True

        # End the streams.
        tasks = []
        for stream, item_group in self._streams:
            tasks.append(stream.async_send_heap(item_group.get_end()))
        await asyncio.gather(*tasks)

    def run(self):
        """Starts the sender."""
        # Create the thread pool.
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._config['num_workers'])

        # Wait to ensure multiple senders can be synchronised.
        now = int(datetime.datetime.utcnow().timestamp())
        start_time = ((now + 29) // 30) * 30
        self._log.info('Waiting until {}'.format(
                       datetime.datetime.fromtimestamp(start_time)))
        while int(datetime.datetime.utcnow().timestamp()) < start_time:
            time.sleep(0.1)

        # Run the event loop.
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._run_loop(executor))
        except KeyboardInterrupt:
            pass
        finally:
            # Send the end of stream message to each stream.
            self._log.info('Shutting down, closing streams...')
            tasks = []
            for stream, item_group in self._streams:
                tasks.append(stream.async_send_heap(item_group.get_end()))
            loop.run_until_complete(asyncio.gather(*tasks))
            self._log.info('... finished.')
            executor.shutdown()
            # loop.close()  # Not required.


def main():
    """Main function for SPEAD sender module."""
    # Check command line arguments.
    if len(sys.argv) != 2:
        raise RuntimeError('Usage: python3 async_send.py <json config>')

    # Set up logging.
    sip_logging.init_logger(show_thread=False)

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
