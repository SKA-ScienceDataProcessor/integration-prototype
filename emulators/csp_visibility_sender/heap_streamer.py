# -*- coding: utf-8 -*-
"""Module to stream SPEAD visibility data."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import spead2
import spead2.send
import numpy as np
import time

class HeapStreamer(object):
    """Class providing methods to set up and send SPEAD heaps"""

    def __init__(self, config, frame_shape, log):
        """Constructor. Creates SPEAD streams and ItemGroups."""
        self.config = config
        self.frame_shape = frame_shape
        self.log = log
        self.heap_descriptor = self._init_heap_descriptor()
        self.payload = self._init_payload()
        self.streams = list()
        self.heap_counter = 0
        self.send_timer = 0
        self.heap_size = self._get_heap_size()
        self._create_streams()

    def start(self):
        """Send the start of stream marker to each stream"""
        self.heap_counter = 0
        self.send_timer = 0
        # Send start-of-stream marker for each stream
        for stream, item_group in self.streams:
            stream.send_heap(item_group.get_start())

    def end(self):
        """Send the end of stream marker to each stream"""
        # Send a end-of-stream marker for each stream
        for stream, item_group in self.streams:
            stream.send_heap(item_group.get_end())

    def send_heap(self, heap_index, stream_id=0):
        """Send a heap with the data in self.payload"""
        self.log.debug('  heap_descriptor {:03d}'.format(heap_index))
        # Update the values of items in the item group for this stream.
        t0 = time.time()
        stream, item_group = self.streams[stream_id]
        for name, item in item_group.items():
            self.log.debug('    item: 0x{:04X} {}'.format(item.id, name))
            item.value = self.payload[name]
        # Send the updated heap_descriptor
        _heap = item_group.get_heap()
        stream.send_heap(_heap)
        self.heap_counter += 1
        self.send_timer += (time.time() - t0)

    def log_stats(self):
        """Print (to the log) the stats for sending heaps"""
        # Print some performance statistics.
        total_bytes = self.heap_size * self.heap_counter
        total_time = self.send_timer
        self.log.info('Sending complete in {} s'.format(total_time))
        self.log.info('Total bytes = {} ({:.3f} MiB)'.
                      format(total_bytes, total_bytes / 1024**2))
        self.log.info('Rate = {:.3f} MiB/s'
                      .format(total_bytes / (1024**2 * total_time)))

    def _get_heap_size(self):
        """Return the total size of items in the SPEAD heap in bytes."""
        heap_size = 0
        for item in self.heap_descriptor:
            num_elements = np.prod(item['shape'])
            if 'type' in item:
                heap_size += np.dtype(item['type']).itemsize * num_elements
            elif 'format' in item:
                item_bits = sum(bits for _, bits in item['format'])
                heap_size += item_bits // 8 * num_elements
        return heap_size

    @staticmethod
    def _get_config_r(settings, key, default=None):
        """Read a configuration value from a settings dictionary"""
        value = default
        if len(key) == 1:
            if key[0] in settings:
                value = settings[key[0]]
        else:
            if key[0] in settings:
                return HeapStreamer._get_config_r(settings[key[0]], key[1:],
                                                  default)
        return value

    def _get_config(self, key, default=None):
        """Read a configuration value"""
        return self._get_config_r(self.config, key, default)

    def _create_streams(self):
        """Construct streams, item group and item descriptions."""
        # Construct the SPEAD flavour description
        parent = 'spead_flavour'
        version = self._get_config([parent, 'version'], 4)
        item_pointer_bits = self._get_config([parent, 'item_pointer_bits'], 64)
        heap_address_bits = self._get_config([parent, 'heap_address_bits'], 40)
        bug_compat_mask = self._get_config([parent, 'bug_compat_mask'], 0)
        flavour = spead2.Flavour(version, item_pointer_bits, heap_address_bits,
                                 bug_compat_mask)

        # Construct UDP stream objects and associated heap_descriptor item
        # groups.
        streams = list()
        for i, stream in enumerate(self.config['sender_node']['streams']):
            host = stream['host']
            port = stream['port']
            rate = stream['rate'] if 'rate' in stream else 0
            threads = stream['threads'] if 'threads' in stream else 1
            stream_config = spead2.send.StreamConfig(rate=rate)
            thread_pool = spead2.ThreadPool(threads=threads)
            stream = spead2.send.UdpStream(thread_pool, host, port,
                                           stream_config)
            item_group = spead2.send.ItemGroup(flavour=flavour)

            # Append stream & item group the stream list.
            streams.append((stream, item_group))

            self.log.debug('Configuring stream {}:'.format(i))
            self.log.debug('  Address = {}:{}'.format(host, port))
            self.log.debug('  Flavour = SPEAD-{}-{} v{} compat:{}'.
                           format(flavour.item_pointer_bits,
                                  flavour.heap_address_bits,
                                  flavour.version,
                                  flavour.bug_compat))
            self.log.debug('  Threads = {}'.format(threads))
            self.log.debug('  Rate    = {}'.format(rate))

            # Add items to the item group based on the heap_descriptor
            for j, item in enumerate(self.heap_descriptor):
                item_id = item['id']
                if isinstance(item_id, str):
                    item_id = int(item_id, 0)
                name = item['name']
                desc = item['description']
                item_type = item['type'] if 'type' in item else None
                item_format = item['format'] if 'format' in item else None
                if 'shape' not in item:
                    raise RuntimeError('shape not defined for {}'.format(name))
                shape = item['shape']
                item_group.add_item(item_id, name, desc, shape=shape,
                                    dtype=item_type, format=item_format)
                self.log.debug('Adding item {} : {} {}'.format(j, item_id,
                                                               name))
                self.log.debug('  description = {}'.format(desc))
                if item_type is not None:
                    self.log.debug('  type = {}'.format(item_type))
                if item_format is not None:
                    self.log.debug('  format = {}'.format(item_format))
                    self.log.debug('  shape = {}'.format(shape))

        self.streams = streams

    def _init_heap_descriptor(self):
        """Return the heap descriptor dictionary."""
        heap_descriptor = [
            # Per SPEAD heap_descriptor
            {
                "id": 0x0045,
                "name": "timestamp_utc",
                "description": "SDP_REQ_INT-45.",
                "format": [('u', 32), ('u', 32)],
                "shape": (1,)
            },
            {
                "id": 0x0046,
                "name": "channel_baseline_id",
                "description": "SDP_REQ_INT-46",
                "format": [('u', 26), ('u', 22)],
                "shape": (1,)
            },
            {
                "id": 0x0047,
                "name": "channel_baseline_count",
                "description": "SDP_REQ_INT-47",
                "format": [('u', 26), ('u', 22)],
                "shape": (1,)
            },
            {
                "id": 0x0048,
                "name": "schedule_block",
                "description": "SDP_REQ_INT-48",
                "type": "u8",
                "shape": (1,)
            },
            {
                "id": 0x0049,
                "name": "hardware_source_id",
                "description": "SDP_REQ_INT-49",
                "format": [('u', 24)],
                "shape": (1,)
            },
            # Per visibility data
            {
                "id": 0x0050,
                "name": "time_centroid_index",
                "description": "SDP_REQ_INT-50",
                "format": [('u', 8)],
                "shape": self.frame_shape
            },
            {
                "id": 0x0051,
                "name": "complex_visibility",
                "description": "SDP_REQ_INT-51",
                "format": [('f', 32), ('f', 32)],
                "shape": self.frame_shape
            },
            {
                "id": 0x0052,
                "name": "flagging_fraction",
                "description": "SDP_REQ_INT-52",
                "format": [('u', 8)],
                "shape": self.frame_shape
            }
        ]
        return heap_descriptor

    def _init_payload(self):
        """Return an empty payload"""
        payload = dict(
            timestamp_utc=[(0, 0)],
            channel_baseline_id=[(0, 0)],
            channel_baseline_count=[(0, 0)],
            schedule_block=[0],
            hardware_source_id=[0],
            complex_visibility=np.zeros(self.frame_shape),
            time_centroid_index=np.ones(self.frame_shape, dtype=np.uint8),
            flagging_fraction=np.ones(self.frame_shape, dtype=np.uint8)
        )
        return payload
