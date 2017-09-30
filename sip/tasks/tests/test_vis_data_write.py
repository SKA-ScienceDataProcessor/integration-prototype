# -*- coding: utf-8 -*-
""" FIXME(BM) Missing module description!

Run with:
    $ python3 -m unittest -f -v sip.tasks.test.test_vis_data_write
or
    $ python3 -m unittest discover -f -v -p test_vis_data_write.py
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import glob
import os
import pickle
import unittest

import numpy

OSKAR = None
# Comment out 'try' block to not write Measurement Sets.
# try:
#     import oskar
# except ImportError:
#     oskar = None


def create_heap(header, start_time, start_chan, end_chan):
    """ Creates a visibility data dictionary.

    Data dimensions:
        [sub_arrays (1), beams (1), channels, baselines, pols]

    Args:
        header (dict): Visibility header dictionary.
        start_time (int): Visibility data block start time index.
        start_chan (int): Visibility start channel index.
        end_chan (int): Visibility end channel index.

    Returns:
        dict: Visibility data heap consisting of the 'data' and two meta-data
        fields, 'start_time' and 'start_channel'.
    """
    num_stations = header['num_stations']
    num_chan = end_chan - start_chan + 1
    num_baselines = num_stations * (num_stations - 1) // 2
    num_pols = header['num_pols']
    data = numpy.zeros([1, 1, num_chan, num_baselines, num_pols], dtype='c8')

    # Fill with pattern.
    for chan in range(num_chan):
        data[:, :, chan, :, :].real = start_time
        data[:, :, chan, :, :].imag = chan + start_chan

    # Return a dictionary containing the heap data.
    return {'start_time': start_time, 'start_chan': start_chan, 'data': data}


def ms_create(filename, header, file_start_chan, file_num_chan):
    """ Create a Measurement Set.
    """
    # pylint: disable=R1705
    if OSKAR:
        channel_width_hz = header['channel_width_hz']
        start_freq_hz = header['start_frequency_hz'] + (
            channel_width_hz * file_start_chan)
        return OSKAR.MeasurementSet.create(
            filename, header['num_stations'], file_num_chan,
            header['num_pols'], start_freq_hz, channel_width_hz)
    else:
        return None


def ms_open(filename):
    """ Open a Measurement Set
    """
    return OSKAR.MeasurementSet.open(filename) if OSKAR else None


def ms_write(measurement_set, file_start_time, file_start_chan, heap):
    """ Write a Measurement Set.
    """
    if OSKAR:
        vis_shape = heap['data'].shape
        num_chan = vis_shape[2]
        num_baselines = vis_shape[3]
        start_chan = heap['start_chan'] - file_start_chan
        start_time = heap['start_time'] - file_start_time
        start_row = num_baselines * start_time
        measurement_set.write_vis(start_row, start_chan, num_chan,
                                  num_baselines, heap['data'][0, 0, :, :, :])
    else:
        pass


def pickle_write(filename, data):
    """ Write a pickle file.
    """
    with open(filename, 'ab') as file:
        pickle.dump(data, file, protocol=2)


def pickle_read(filename):
    """" Read a pickle file.
    """
    with open(filename, 'rb') as file:
        while True:
            try:
                yield pickle.load(file)
            except EOFError:
                break


class TestVisData(unittest.TestCase):
    """ Unit tests for receiving visibility data.
    """

    def test(self):
        """ Test method.

        Mocks the receive of visibility data writing the data received
        to a set of pickle files.
        """
        # pylint: disable=R0914,R0912,R0915
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
        num_heaps_chan = ((num_chan + heap_max_num_chan - 1) //
                          heap_max_num_chan)
        num_heaps_time = num_time
        num_heaps = num_heaps_chan * num_heaps_time

        # Loop over heaps (this is the "send/receive" loop).
        measurement_sets = {}
        for heap_index in range(num_heaps):
            # Get the time and channel range for this heap.
            heap_start_time = heap_index // num_heaps_chan
            heap_start_chan = (heap_index % num_heaps_chan) * heap_max_num_chan
            heap_end_chan = heap_start_chan + heap_max_num_chan - 1
            if heap_end_chan >= num_chan:
                heap_end_chan = num_chan - 1

            # Create a filled heap (i.e. "send").
            heap = create_heap(hdr, heap_start_time, heap_start_chan,
                               heap_end_chan)

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
            base_name = 'test_vis_T%04d-%04d_C%04d-%04d' % (
                file_start_time, file_end_time, file_start_chan, file_end_chan)

            # Write header if the file doesn't exist, then write the heap.
            pickle_file = base_name + '.p'
            if not os.path.isfile(pickle_file):
                pickle_write(pickle_file, hdr)
            pickle_write(pickle_file, heap)

            # Write to Measurement Set if required.
            ms_name = base_name + '.ms'
            if ms_name not in measurement_sets:
                # Don't open too many files at once.
                if len(measurement_sets.items()) > 5:
                    measurement_sets.popitem()
                measurement_sets[ms_name] = ms_create(
                    ms_name, hdr, file_start_chan, file_num_chan) \
                    if not os.path.isdir(ms_name) else ms_open(ms_name)
            ms_write(measurement_sets[ms_name], file_start_time,
                     file_start_chan, heap)

        # Test that heaps have been received and written correctly.
        # Get a list of all 'vis_' pickle files.
        file_list = glob.glob('test_vis_*.p')
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
                    for channel in range(num_chan):
                        channel_data = vis_data[:, :, channel, :, :]
                        self.assertTrue((channel_data.real == start_time)
                                        .any())
                        self.assertTrue((channel_data.imag ==
                                         channel + start_chan).any())

        # Clean up visibility files
        for file in file_list:
            os.remove(file)
