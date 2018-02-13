# -*- coding: utf-8 -*-
"""Module to stream SPEAD visibility data.

The visibility data is sent as a number of SPEAD heaps, with a have a structure
(payload) defined in the CSP-SDP ICD documents. Heaps are sent to a stream
which is a UDP socket.
"""
import logging
import time

import numpy as np
import spead2
import spead2.send

from .heap_descriptor import get_heap_descriptor


class HeapStreamer:
    """Class for sending SPEAD heaps to one or more SPEAD streams (UDP sockets).

    Streams are configured according to a python dictionary passed to the
    constructor. The content of the data sent in each heap (the payload)
    is defined in the relevant CSP-SDP ICD documents.

    Usage example::

        config = dict(sender_node=[])
        frame_shape = (1, 1, 1, 435, 4)
        streamer = HeapStreamer(config, frame_shape)
        streamer.start()
        for i in range(num_heaps):
            streamer.payload['timestamp_utc'] = [(i, 0)]
            streamer.payload['complex_visibility'] = get_vis_data(i)
            streamer.send_heap(i)
        streamer.end()
    """

    def __init__(self, config, frame_shape):
        """Creates and sets up SPEAD streams.

        The configuration of streams is passed in via the ``config`` argument.

        The dimensions of the visibility data (frame shape) should be provided
        in order to initialise the payload. This is a tuple defined as follows:

            (1, 1, num_channels, num_baselines, 4)

        where num_channels and num_baselines are the number of channels
        and number of baselines per stream heap.

        Args:
            config (dict): Dictionary of settings (see above).
            frame_shape (tuple): Dimensions of the payload visibility data.
        """
        self._config = config
        self._frame_shape = frame_shape
        self._heap_counter = 0
        self._send_timer = 0
        self._heap_size = self._get_heap_size()
        self._streams = self._create_streams()
        self._payload = self._init_payload()

    def start(self):
        """Send the start of stream message to each stream."""
        self._heap_counter = 0
        self._send_timer = 0
        for stream, item_group in self._streams:
            stream.send_heap(item_group.get_start())

    def end(self):
        """Send the end of stream message to each stream."""
        for stream, item_group in self._streams:
            stream.send_heap(item_group.get_end())

    def send_heap(self, heap_index, stream_id=0):
        """Send one heap with the data contained in self.payload to the
        specified stream ID.

        Args:
            heap_index (int): HEAP index.
            stream_id (int): Stream index (default=0).
        """
        log = logging.getLogger(__name__)
        log.debug('sending heap %03i', heap_index)
        # Update the values of items in the item group for this stream.
        timer = time.time()
        stream, item_group = self._streams[stream_id]
        for name, item in item_group.items():
            log.debug(f' adding item from payload: 0x{item.id:04X} {name}')
            item.value = self._payload[name]
        # Send the updated heap_descriptor
        _heap = item_group.get_heap()
        stream.send_heap(_heap)
        self._heap_counter += 1
        self._send_timer += (time.time() - timer)

    @property
    def streams(self):
        """Streams attribute.

        This is a list of SPEAD streams.
        """
        return self._streams

    @property
    def payload(self):
        """Payload attribute.

        This is a dictionary containing the payload for the HEAP.
        This dictionary should be modified before calling send_heap() to
        update the data sent.

        Payload has the following keys

        * timestamp_utc
        * channel_baseline_id
        * channel_baseline_count
        * schedule_block
        * hardware_source_id
        * complex_visibility
        * time_centroid_index
        * flagging_fraction
        """
        return self._payload

    # @payload.setter
    # def payload(self, **kwargs):
    #     print(kwargs)

    @payload.deleter
    def payload(self):
        del self._payload

    def log_stats(self):
        """Print (to the log) the stats for sending heaps"""
        # Print some performance statistics.
        log = logging.getLogger(__name__)
        total_bytes = self._heap_size * self._heap_counter
        total_time = self._send_timer
        log.info('Sending complete in %.2f s', total_time)
        log.info('Total bytes = %i (%.3f MiB)', total_bytes,
                 total_bytes / 1024**2)
        log.info('Rate = %.3f MiB/s', total_bytes / (1024**2 * total_time))

    def _get_heap_size(self):
        """Return the total size of items in the SPEAD heap in bytes."""
        heap_size = 0
        for item in get_heap_descriptor(self._frame_shape):
            num_elements = np.prod(item['shape'])
            if 'type' in item:
                heap_size += np.dtype(item['type']).itemsize * num_elements
            elif 'format' in item:
                item_bits = sum(bits for _, bits in item['format'])
                heap_size += item_bits // 8 * num_elements
        return heap_size

    @staticmethod
    def _create_stream(config, flavour, heap_descriptor):
        """Construct a single stream."""
        log = logging.getLogger(__name__)

        # Create the item group for the stream
        item_group = spead2.send.ItemGroup(flavour=flavour)
        for item in heap_descriptor:
            _item = item_group.add_item(
                item['id'], item['name'], item['description'],
                shape=item['shape'], dtype=item.get('type'),
                format=item.get('format'))
            log.debug('Added item: 0x%04X (%s)', _item.id, _item.name)
            log.debug('  description = %s', _item.description)
            log.debug('  format = %s', _item.format)
            log.debug('  type   = %s', _item.dtype)
            log.debug('  shape  = %s', _item.shape)

        # Create stream object
        threads = config.get('threads', 1)
        stream = spead2.send.UdpStream(spead2.ThreadPool(threads=threads),
                                       config.get('host'), config.get('port'),
                                       spead2.send.StreamConfig(rate=0))

        # Return the stream and item group
        return stream, item_group

    def _create_streams(self):
        """Construct streams, item group and item descriptions."""
        # Construct the SPEAD flavour description
        log = logging.getLogger(__name__)

        # Define the SPEAD flavour
        flavour_config = self._config.get('spead_flavour')
        flavour = spead2.Flavour(flavour_config.get('version', 4),
                                 flavour_config.get('item_pointer_bits', 64),
                                 flavour_config.get('heap_address_bits', 40),
                                 flavour_config.get('bug_compat_mask', 0))
        log.debug('Using SPEAD flavour = SPEAD-%d-%d v%d compat:%d',
                  flavour.item_pointer_bits, flavour.heap_address_bits,
                  flavour.version, flavour.bug_compat)

        # Create SPEAD streams
        streams_config = self._config.get('sender_node').get('streams')
        descriptor = get_heap_descriptor(self._frame_shape)
        streams = list()
        for i, config in enumerate(streams_config):
            log.debug('Configuring stream %d:', i)
            log.debug('  Address = %s:%d', config.get('host'),
                      config.get('port'))
            log.debug('  Threads = %d', config.get('threads', 1))
            streams.append(self._create_stream(config, flavour, descriptor))

        return streams

    def _init_payload(self):
        """Return an empty payload"""
        payload = dict(
            timestamp_utc=[(0, 0)],
            channel_baseline_id=[(0, 0)],
            channel_baseline_count=[(0, 0)],
            schedule_block=[0],
            hardware_source_id=[0],
            complex_visibility=np.zeros(self._frame_shape, dtype='c8'),
            time_centroid_index=np.ones(self._frame_shape, dtype='u1'),
            flagging_fraction=np.ones(self._frame_shape, dtype='u1')
        )
        return payload
