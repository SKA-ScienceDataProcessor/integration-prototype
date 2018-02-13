# -*- coding: utf-8 -*-
"""Module for simulation of visibility data.

This module makes use of the HeapStreamer class to send the visibility data.
"""
import numpy as np

from .heap_streamer import HeapStreamer


class SimpleSimulator:
    """Very simple simulation class used to stream SPEAD heaps.

    SPEAD heaps contain simple patterns.
    """
    def __init__(self, config, log):
        """
        Creates and initialises the visibility simulator.

        Args:
            config (dict): Dictionary of settings
            log (logging.Logger): Python logging object
        """
        _obs = config['observation']
        self.log = log
        self.config = config
        self.num_stations = _obs['num_stations']
        self.num_pol = _obs['num_pol']
        self.num_baselines = self.num_stations * (self.num_stations - 1) // 2
        self.num_times = _obs['num_times']
        self.total_channels = _obs['num_channels']
        self.sender_start_channel = config['sender_node']['start_channel']
        self.num_streams = len(config['sender_node']['streams'])
        self.stream_num_channels = self.total_channels // self.num_streams
        self.frame_shape = (self.num_baselines,)
        self.log.debug('Number of channels per heap_descriptor = {}'.
                       format(self.stream_num_channels))
        self.log.debug('Number of baselines = {}'.format(self.num_baselines))
        self.log.debug('Frame shape = {}'.format(self.frame_shape))
        self.log.debug('Number of polarization = {}'.format(self.num_pol))

    def simulate_heaps(self):
        """Simulate and send a stream of heaps using the specified
        HeapStreamer.
        """
        streamer = HeapStreamer(self.log, self.config, self.num_pol,
                                self.num_baselines, self.frame_shape)
        streamer.start()

        num_streams = len(streamer._streams)
        assert num_streams == self.num_streams

        self.log.info('Starting simulation...')
        self.log.info('  * No. times = {}'.format(self.num_times))
        self.log.info('  * No. channels (per stream) = {}'.
                      format(self.stream_num_channels))
        self.log.info('  * Start channel = {}'.
                      format(self.sender_start_channel))
        self.log.info('  * No. streams = {}'.format(self.num_streams))

        for t in range(self.num_times):
            self.log.debug('== Time {:03d}/{:03d} =='.format(t + 1,
                                                             self.num_times))

            # Loop over heap stream.
            for j in range(num_streams):
                c0 = self.sender_start_channel + j * self.stream_num_channels
                c1 = c0 + self.stream_num_channels
                stream, heap = streamer._streams[j]
                vis_data = np.ones(self.frame_shape, dtype= \
                    [('TCI', 'i8'), ('FD', 'u8'), ('VIS', 'c8', self.num_pol)])
                self.log.debug('>> Channels = {} <<'.format(range(c0, c1)))

                for c in range(c0, c1):
                    vis_data['TCI'] = np.ones(self.num_baselines, dtype="i8")
                    vis_data['FD'] = 5 * np.ones(self.num_baselines, dtype="i8")
                    vis_data['VIS'] = 10 * np.ones((self.num_baselines, self.num_pol), dtype="c8")

                # Adding data to the heap
                heap['visibility_channel_count'].value = (self.stream_num_channels,)
                heap['visibility_channel_id'].value = (c0,)
                heap['correlator_output_data'].value = vis_data
                streamer.send_heap(heap_index=t, stream_id=j)

        streamer.end()
        streamer.log_stats()
