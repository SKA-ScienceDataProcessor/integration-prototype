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
        self.num_channels = config['sender_node']['num_channels']
        self.frame_shape = (1, 1, self.num_channels, self.num_baselines, 4)
        self.log.debug('Number of channels per heap_descriptor = {}'.
                       format(self.num_channels))
        self.log.debug('Number of baselines = {}'.format(self.num_baselines))

    def simulate_heaps(self, streamer: HeapStreamer):
        """Simulate and send a stream of heaps."""
        streamer.start()
        num_streams = len(streamer.streams)

        self.log.info('Starting simulation...')
        self.log.info('  * Number of times = {}'.format(self.num_times))
        self.log.info('  * Number of channels = {}'.format(self.num_channels))

        streamer.start()  # FIXME(BM) not sure this is needed.

        for i in range(self.num_times):
            # Loop over heap stream. a heap stream contains 1 or more channels.
            for j in range(num_streams):
                channel_start = 0
                for c in range(channel_start, channel_start + self.num_channels):
                    streamer.payload['complex_visibility'] = \
                        np.ones(streamer.frame_shape) * i
                    streamer.payload['timestamp_utc'] = [(i, i + 3)]
                    streamer.send_heap(heap_index=i, stream_id=j)

        streamer.end()
        streamer.log_stats()
