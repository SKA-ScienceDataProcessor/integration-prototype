# -*- coding: utf-8 -*-
"""Module for simulation of visibility data.

This module makes use of the HeapStreamer class to send the visibility data.
"""
import logging

import numpy as np

from .heap_streamer import HeapStreamer


class SimpleSimulator:
    """Very simple simulation class used to stream SPEAD heaps.

    SPEAD heaps contain simple patterns.
    """

    def __init__(self, config):
        """
        Creates and initialises the visibility simulator.

        Args:
            config (dict): Dictionary of emulator configuration settings
        """
        self._config = config
        num_stations = config['observation']['num_stations']
        total_channels = config['observation']['num_channels']
        num_streams = len(config['sender_node']['streams'])
        num_baselines = num_stations * (num_stations - 1) // 2
        stream_num_channels = total_channels // num_streams
        self.frame_shape = (1, 1, stream_num_channels, num_baselines, 4)

    def _stream_channels(self, stream_index):
        """Returns channels for the specified stream"""
        streams_spec = self._config.get('sender_node').get('streams')
        num_streams = len(streams_spec)
        total_channels = self._config.get('observation').get('num_channels')
        stream_num_channels = total_channels // num_streams
        sender_start_channel = self._config['sender_node']['start_channel']
        start = sender_start_channel + stream_index * stream_num_channels
        end = start + stream_num_channels
        return range(start, end)

    def simulate_heaps(self, streamer: HeapStreamer):
        """Simulate and send a stream of heaps using the specified
        HeapStreamer.

        Args:
            streamer (HeapStreamer): SPEAD heap streamer class.
        """
        obs = self._config.get('observation')
        assert obs is not None
        num_times = obs.get('num_times')
        num_streams = len(streamer.streams)
        num_channels = obs.get('num_channels') // num_streams
        start_channel = self._config['sender_node']['start_channel']

        log = logging.getLogger(__name__)
        log.info('Starting simulation...')
        log.info('  * No. times = %d', num_times)
        log.info('  * No. channels (per stream) = %d', num_channels)
        log.info('  * Start channel = %d', start_channel)
        log.info('  * No. streams = %d', num_streams)

        streamer.start()

        for time in range(num_times):
            log.debug('== Time {%03d}/{%03d} ==', time + 1,
                      num_times)
            streamer.payload['timestamp_utc'] = [(time, time + 3)]

            # Loop over streams and simulate heap payloads.
            for j in range(num_streams):
                stream_channels = self._stream_channels(j)
                streamer.payload['channel_baseline_count'] = \
                    [(num_channels, 0)]
                streamer.payload['channel_baseline_id'] = \
                    [(stream_channels[0], 0)]
                vis_data = np.ones(self.frame_shape, dtype='c8')
                log.debug('>> Channels = %s <<', stream_channels)
                # For each channel in the heap.
                for channel in stream_channels:
                    vis_data[:, :, channel, :, :].real = time
                    vis_data[:, :, channel, :, :].imag = channel
                streamer.payload['complex_visibility'] = vis_data
                streamer.send_heap(heap_index=time, stream_id=j)

        streamer.end()
        streamer.log_stats()
