# -*- coding: utf-8 -*-
"""Module to provide simulation of visibility data."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from emulators.csp_visibility_sender.heap_streamer import HeapStreamer
import numpy as np


class Simulator(object):
    """Simulation class used to stream SPEAD heaps"""

    def __init__(self, config, log):
        _obs = config['observation']
        _tel = _obs['telescope']
        self.log = log
        self.config = config
        self.num_baselines = _tel['num_baselines']
        self.num_times = _obs['time']['num_times']
        self.total_channels = _obs['frequency']['num_channels']
        self.sender_start_channel = config['sender_node']['start_channel']
        self.num_streams = len(config['sender_node']['streams'])
        self.stream_num_channels = self.total_channels // self.num_streams
        self.frame_shape = (1, 1, self.stream_num_channels, self.num_baselines, 4)
        self.log.debug('Number of channels per heap_descriptor = {}'.
                       format(self.stream_num_channels))
        self.log.debug('Number of baselines = {}'.format(self.num_baselines))

    def simulate_heaps(self, streamer: HeapStreamer):
        """Simulate and send a stream of heaps."""
        num_streams = len(streamer.streams)
        assert(num_streams == self.num_streams)

        self.log.info('Starting simulation...')
        self.log.info('  * No. times = {}'.format(self.num_times))
        self.log.info('  * No. channels (per stream) = {}'.
                      format(self.stream_num_channels))
        self.log.info('  * Start channel = {}'.format(self.sender_start_channel))
        self.log.info('  * No. streams = {}'.format(self.num_streams))

        streamer.start()

        for t in range(self.num_times):
            self.log.debug('== Time {:03d}/{:03d} =='.format(t + 1,
                                                             self.num_times))
            streamer.payload['timestamp_utc'] = [(t, t + 3)]

            # Loop over heap stream. a heap stream contains 1 or more channels.
            for j in range(num_streams):
                c0 = self.sender_start_channel + j * self.stream_num_channels
                c1 = c0 + self.stream_num_channels
                streamer.payload['channel_baseline_count'] = \
                    [(self.stream_num_channels, 0)]
                streamer.payload['channel_baseline_id'] = [(c0, 0)]
                vis_data = np.ones(self.frame_shape, dtype=np.complex64)
                self.log.debug('>> Channels = {} <<'.format(range(c0, c1)))
                for c in range(c0, c1):
                    vis_data[:, :, c, :, :].real = t
                    vis_data[:, :, c, :, :].imag = c
                streamer.payload['complex_visibility'] = vis_data
                streamer.send_heap(heap_index=t, stream_id=j)

        streamer.end()
        streamer.log_stats()
