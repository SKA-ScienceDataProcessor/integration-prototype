# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import spead2
import spead2.recv
import sys
import logging
import numpy
import glob
import time
import argparse
import simplejson as json
import os
import pickle

oskar = None
# Comment out 'try' block to not write Measurement Sets.
# try:
#     import oskar
# except ImportError:
#     oskar = None


def _init_log(level=logging.DEBUG):
    """Initialise the logging object."""
    log = logging.getLogger(__file__)
    log.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s: %(message)s',
                                  '%Y/%m/%d-%H:%M:%S')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    return log


def _parse_command_line():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Receive fake visibility data using the SPEAD protocol.')
    parser.add_argument('config_file', type=argparse.FileType('r'),
                        help='JSON configuration file..')
    parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                        action='store_true')
    parser.add_argument('-p', '--print_settings', help='Print settings file.',
                        action='store_true')
    return parser.parse_args()


def _create_streams(config, log):
    """Construct streams, item group and item descriptions."""
    # bug_compat = spead2.BUG_COMPAT_PYSPEAD_0_5_2
    bug_compat = 0
    lower = config['memory_pool']['lower']
    upper = config['memory_pool']['upper']
    max_free = config['memory_pool']['max_free']
    initial = config['memory_pool']['initial']
    streams = []
    for stream in config['streams']:
        log.debug('Creating stream on port {}'.format(stream['port']))
        s = spead2.recv.Stream(spead2.ThreadPool(), bug_compat)
        pool = spead2.MemoryPool(lower, upper, max_free, initial)
        s.set_memory_allocator(pool)
        s.add_udp_reader(stream['port'])
        streams.append(s)
    return streams


def _ms_create(filename, config, file_start_chan, file_num_chan):
    if oskar:
        channel_width_hz = config['observation']['channel_width_hz']
        start_freq_hz = config['observation']['start_frequency_hz'] + (
            channel_width_hz * file_start_chan)
        return oskar.MeasurementSet.create(
            filename, config['num_stations'], file_num_chan,
            config['num_pols'], start_freq_hz, channel_width_hz)
    else:
        return None


def _ms_open(filename):
    return oskar.MeasurementSet.open(filename) if oskar else None


def _ms_write(ms, file_start_time, file_start_chan, data):
    if oskar:
        num_chan = data['complex_visibility'].shape[2]
        num_baselines = data['complex_visibility'].shape[3]
        start_chan = data['channel_baseline_id'][0][0] - file_start_chan
        time_index = data['time_index'] - file_start_time
        start_row = num_baselines * time_index
        ms.write_vis(start_row, start_chan, num_chan,
                     num_baselines, data['complex_visibility'][0, 0, :, :, :])
    else:
        pass


def _pickle_write(filename, data):
    with open(filename, 'ab') as f:
        pickle.dump(data, f, protocol=2)


def _receive_heaps(config, streams, log):
    ms = {}
    for stream in streams:
        item_group = spead2.ItemGroup()

        # Loop over all heaps in the stream.
        for heap in stream:
            log.info("Received heap {}".format(heap.cnt))

            # Extract data from the heap into a dictionary.
            data = {}
            items = item_group.update(heap)
            for item in items.values():
                data[item.name] = item.value

            # Skip if the heap does not contain visibilities.
            if 'complex_visibility' not in data:
                continue

            # Get data dimensions.
            time_index = heap.cnt - 2  # Extra -1 because first heap is empty.
            start_channel = data['channel_baseline_id'][0][0]
            num_channels = data['channel_baseline_count'][0][0]
            max_times_per_file = config['output']['max_times_per_file']

            # Find out which file this heap goes in.
            # Get the time and channel range for the file.
            file_start_time = (time_index // max_times_per_file) * \
                              max_times_per_file
            file_end_time = file_start_time + max_times_per_file - 1

            # Construct filename.
            base_name = 'vis_T%04d-%04d_C%04d-%04d' % (
                file_start_time, file_end_time,
                start_channel, start_channel + num_channels - 1)
            data['time_index'] = time_index

            # Write visibility data.
            _pickle_write(base_name + '.p', data)

            # Write to Measurement Set if required.
            ms_name = base_name + '.ms'
            if ms_name not in ms:
                if len(ms) > 5:
                    ms.popitem()  # Don't open too many files at once.
                ms[ms_name] = _ms_create(
                    ms_name, config, start_channel, num_channels) \
                    if not os.path.isdir(ms_name) else _ms_open(ms_name)
            _ms_write(ms[ms_name], file_start_time, start_channel, data)

        # Stop the stream when there are no more heaps.
        stream.stop()


def _pickle_read(filename):
    with open(filename, 'rb') as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def main():
    """Main script function"""
    # Parse command line arguments
    args = _parse_command_line()

    # Initialise logging.
    log = _init_log(level=logging.DEBUG if args.verbose else logging.INFO)

    # Load configuration.
    log.info('Loading config: {}'.format(args.config_file.name))
    config = json.load(args.config_file)
    if args.print_settings:
        log.debug('Settings:\n {}'.format(json.dumps(config, indent=4,
                                                     sort_keys=True)))

    # Create streams and receive data.
    log.info('Creating streams...')
    streams = _create_streams(config, log)
    log.info('Waiting to receive...')
    _receive_heaps(config, streams, log)

    # Test that heaps have been received and written correctly.
    # Get a list of all 'vis_' pickle files.
    log.info('Checking data...')
    file_list = glob.glob('vis_*.p')
    for file_name in file_list:
        # Read the heaps in the file.
        heaps = _pickle_read(file_name)
        for (i, heap) in enumerate(heaps):
            vis_data = heap['complex_visibility']
            time_index = heap['time_index']
            start_chan = heap['channel_baseline_id'][0][0]

            # Check pattern.
            for c in range(vis_data.shape[2]):
                assert (numpy.array(vis_data[:, :, c, :, :].real ==
                                    time_index).all())
                assert (numpy.array(vis_data[:, :, c, :, :].imag ==
                                    c + start_chan).all())
    log.info('Done.')

if __name__ == '__main__':
    main()
