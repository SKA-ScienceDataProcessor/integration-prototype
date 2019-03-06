# -*- coding: utf-8 -*-
"""Sends test data using spead2."""

import time
import numpy

import spead2
import spead2.send


def main():
    """Runs the test sender."""
    stream_config = spead2.send.StreamConfig(
        max_packet_size=16356, rate=1000e6, burst_size=10, max_heaps=1)
    item_group = spead2.send.ItemGroup(flavour=spead2.Flavour(4, 64, 48, 0))

    # Add item descriptors to the heap.
    num_baselines = (512 * 513) // 2
    dtype = [('TCI', 'i1'), ('FD', 'u1'), ('VIS', '<c8', 4)]
    item_group.add_item(
        id=0x6000, name='visibility_timestamp_count', description='',
        shape=tuple(), format=None, dtype='<u4')
    item_group.add_item(
        id=0x6001, name='visibility_timestamp_fraction', description='',
        shape=tuple(), format=None, dtype='<u4')
    item_group.add_item(
        id=0x6005, name='visibility_baseline_count', description='',
        shape=tuple(), format=None, dtype='<u4')
    item_group.add_item(
        id=0x6008, name='scan_id', description='',
        shape=tuple(), format=None, dtype='<u8')
    item_group.add_item(
        id=0x600A, name='correlator_output_data', description='',
        shape=(num_baselines,), dtype=dtype)

    # Create streams and send start-of-stream message.
    streams = []
    num_streams = 2
    for i in range(num_streams):
        stream = spead2.send.UdpStream(
            thread_pool=spead2.ThreadPool(threads=1),
            hostname='127.0.0.1', port=41000 + i, config=stream_config)
        stream.send_heap(item_group.get_start())
        streams.append(stream)

    vis = numpy.zeros(shape=(num_baselines,), dtype=dtype)
    num_heaps = 200
    start_time = time.time()
    for stream in streams:
        # Update values in the heap.
        item_group['visibility_timestamp_count'].value = 1
        item_group['visibility_timestamp_fraction'].value = 0
        item_group['visibility_baseline_count'].value = num_baselines
        item_group['scan_id'].value = 100000000
        item_group['correlator_output_data'].value = vis
        # Iterate heaps.
        for i in range(num_heaps):
            # Send heap.
            stream.send_heap(item_group.get_heap(descriptors='all', data='all'))

    # Print time taken.
    duration = time.time() - start_time
    data_size = num_streams * num_heaps * (vis.nbytes / 1e6)
    print("Sent %.3f MB in %.3f sec (%.3f MB/sec)" % (
        data_size, duration, (data_size/duration)))

    # Send end-of-stream message.
    for stream in streams:
        stream.send_heap(item_group.get_end())


if __name__ == '__main__':
    main()
