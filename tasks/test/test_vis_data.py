# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import glob
import numpy
import os
import pickle

oskar = None
# Comment out 'try' block to not write Measurement Sets.
# try:
#     import oskar
# except ImportError:
#     oskar = None


def create_heap(header, start_time, start_chan, end_chan):
    # Create the visibility data array.
    # Dimensions are:
    # num_sub_arrays (1), num_beams (1), num_channels, num_baselines, num_pols
    num_stations = header['num_stations']
    num_chan = end_chan - start_chan + 1
    num_baselines = num_stations * (num_stations - 1) // 2
    num_pols = header['num_pols']
    data = numpy.zeros([1, 1, num_chan, num_baselines, num_pols], dtype='c8')

    # Fill with pattern.
    for c in range(num_chan):
        data[:, :, c, :, :].real = start_time
        data[:, :, c, :, :].imag = c + start_chan

    # Return a dictionary containing the heap data.
    return {'start_time': start_time, 'start_chan': start_chan, 'data': data}


def ms_create(filename, header, file_start_chan, file_num_chan):
    if oskar:
        channel_width_hz = header['channel_width_hz']
        start_freq_hz = header['start_frequency_hz'] + (
            channel_width_hz * file_start_chan)
        return oskar.MeasurementSet.create(
            filename, header['num_stations'], file_num_chan,
            header['num_pols'], start_freq_hz, channel_width_hz)
    else:
        return None


def ms_open(filename):
    return oskar.MeasurementSet.open(filename) if oskar else None


def ms_write(ms, file_start_time, file_start_chan, heap):
    if oskar:
        vis_shape = heap['data'].shape
        num_chan = vis_shape[2]
        num_baselines = vis_shape[3]
        start_chan = heap['start_chan'] - file_start_chan
        start_time = heap['start_time'] - file_start_time
        start_row = num_baselines * start_time
        ms.write_vis(start_row, start_chan, num_chan,
                     num_baselines, heap['data'][0, 0, :, :, :])
    else:
        pass


def pickle_write(filename, data):
    with open(filename, 'ab') as f:
        pickle.dump(data, f, protocol=2)


def pickle_read(filename):
    with open(filename, 'rb') as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def test():
    # Create a header. (Choose some prime numbers for dimensions.)
    hdr = {
        'heap_max_num_chan': 3,
        'file_max_num_chan': 11,
        'file_max_num_time': 43,
        'num_stations': 3,
        'num_pols': 4,
        'num_chan': 53,
        'num_time': 97,
        'start_frequency_hz': 100e6,
        'channel_width_hz': 5e3,
        'some_other_header_keys': None
    }

    # Get maximum sizes, and adjust max per file as necessary.
    heap_max_num_chan = hdr['heap_max_num_chan']
    file_max_num_chan = hdr['file_max_num_chan']
    file_max_num_time = hdr['file_max_num_time']
    num_chan = hdr['num_chan']
    num_time = hdr['num_time']
    file_max_num_chan = (file_max_num_chan //
                         heap_max_num_chan) * heap_max_num_chan

    # Get the total number of heaps required.
    num_heaps_chan = (num_chan + heap_max_num_chan - 1) // heap_max_num_chan
    num_heaps_time = num_time
    num_heaps = num_heaps_chan * num_heaps_time

    # Loop over heaps (this is the "send/receive" loop).
    ms = {}
    for heap_index in range(num_heaps):
        # Get the time and channel range for this heap.
        heap_start_time = heap_index // num_heaps_chan
        heap_start_chan = (heap_index % num_heaps_chan) * heap_max_num_chan
        heap_end_chan = heap_start_chan + heap_max_num_chan - 1
        if heap_end_chan >= num_chan:
            heap_end_chan = num_chan - 1

        # Create a filled heap (i.e. "send").
        heap = create_heap(hdr, heap_start_time, heap_start_chan, heap_end_chan)

        # Find out which file this heap goes in (i.e. "receive").
        # Get the time and channel range for the file.
        file_start_time = (heap['start_time'] //
                           file_max_num_time) * file_max_num_time
        file_start_chan = (heap['start_chan'] //
                           file_max_num_chan) * file_max_num_chan
        file_end_time = file_start_time + file_max_num_time - 1
        file_end_chan = file_start_chan + file_max_num_chan - 1
        if file_end_time >= num_time:
            file_end_time = num_time - 1
        if file_end_chan >= num_chan:
            file_end_chan = num_chan - 1
        file_num_chan = file_end_chan - file_start_chan + 1

        # Construct filename.
        base_name = 'vis_T%04d-%04d_C%04d-%04d' % (
            file_start_time, file_end_time, file_start_chan, file_end_chan)

        # Write header if the file doesn't exist, then write the heap.
        pickle_file = base_name + '.p'
        if not os.path.isfile(pickle_file):
            pickle_write(pickle_file, hdr)
        pickle_write(pickle_file, heap)

        # Write to Measurement Set if required.
        ms_name = base_name + '.ms'
        if ms_name not in ms:
            if len(ms.items()) > 5:
                ms.popitem()  # Don't open too many files at once.
            ms[ms_name] = ms_create(
                ms_name, hdr, file_start_chan, file_num_chan) \
                if not os.path.isdir(ms_name) else ms_open(ms_name)
        ms_write(ms[ms_name], file_start_time, file_start_chan, heap)

    # Test that heaps have been received and written correctly.
    # Get a list of all 'vis_' pickle files.
    file_list = glob.glob('vis_*.p')
    for file_name in file_list:
        # Read the heaps in the file.
        items = pickle_read(file_name)
        for (i, item) in enumerate(items):
            if i == 0:
                # Read the header if required.
                pass
            else:
                vis_data = item['data']
                vis_shape = vis_data.shape
                start_time = item['start_time']
                start_chan = item['start_chan']
                num_chan = vis_shape[2]

                # Check pattern.
                for c in range(num_chan):
                    assert(numpy.array(vis_data[:, :, c, :, :].real ==
                                       start_time).all())
                    assert(numpy.array(vis_data[:, :, c, :, :].imag ==
                                       c + start_chan).all())


if __name__ == '__main__':
    test()
