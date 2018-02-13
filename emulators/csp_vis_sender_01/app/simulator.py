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
            config (dict): Dictionary of settings
            log (logging.Logger): Python logging object
        """
        self.log_ = logging.getLogger(__name__)
        _obs = config['observation']
        self.config = config
        self.num_stations = _obs['num_stations']
        self.num_baselines = self.num_stations * (self.num_stations - 1) // 2
        self.num_times = _obs['num_times']
        self.total_channels = _obs['num_channels']
        self.sender_start_channel = config['sender_node']['start_channel']
        self.num_streams = len(config['sender_node']['streams'])
        self.stream_num_channels = self.total_channels // self.num_streams
        self.frame_shape = (1, 1, self.stream_num_channels, self.num_baselines,
                            4)
        self.log_.debug('Number of channels per heap_descriptor = %d',
                        self.stream_num_channels)
        self.log_.debug('Number of baselines = %d', self.num_baselines)

    def simulate_heaps(self, streamer: HeapStreamer):
        """Simulate and send a stream of heaps using the specified
        HeapStreamer.

        Args:
            streamer (HeapStreamer): SPEAD heap streamer class.
        """
        num_streams = len(streamer._streams)
        assert(num_streams == self.num_streams)
        self.log_.info('Starting simulation...')
        self.log_.info('  * No. times = %d', self.num_times)
        self.log_.info('  * No. channels (per stream) = %d',
                       self.stream_num_channels)
        self.log_.info('  * Start channel = %d',
                       self.sender_start_channel)
        self.log_.info('  * No. streams = %d', self.num_streams)

        streamer.start()

        for t in range(self.num_times):
            self.log_.debug('== Time {%03d}/{%03d} ==', t + 1, self.num_times)
            streamer._payload['timestamp_utc'] = [(t, t + 3)]

            # Loop over heap stream. a heap stream contains 1 or more channels.
            for j in range(num_streams):
                c0 = self.sender_start_channel + j * self.stream_num_channels
                c1 = c0 + self.stream_num_channels
                streamer._payload['channel_baseline_count'] = \
                    [(self.stream_num_channels, 0)]
                streamer._payload['channel_baseline_id'] = [(c0, 0)]
                vis_data = np.ones(self.frame_shape, dtype='c8')
                self.log_.debug('>> Channels = {} <<'.format(range(c0, c1)))
                for c in range(c0, c1):
                    vis_data[:, :, c, :, :].real = t
                    vis_data[:, :, c, :, :].imag = c
                streamer._payload['complex_visibility'] = vis_data
                streamer.send_heap(heap_index=t, stream_id=j)

        streamer.end()
        streamer.log_stats()
