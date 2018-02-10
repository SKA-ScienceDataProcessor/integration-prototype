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
from redis_client import RedisDatabase
from vis_ingest_calc import VisIngestProcessing
import ast

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
    # parser.add_argument('config_file', type=argparse.FileType('r'),
    #                     help='JSON configuration file..')
    parser.add_argument('-i', '--host', help='IP address of the database')
    parser.add_argument('-p', '--port', help='port of the database')
    parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                        action='store_true')
    parser.add_argument('-s', '--print_settings', help='Print settings file.',
                        action='store_true')
    return parser.parse_args()

def _get_config(redis_api, log):
    """
    Getting a snapshot of configuration data 
    from redis database using redis api
    """
    config = redis_api.hget_all("ingest:visibility_receiver")
    return config


def _create_streams(config, log):
    """Construct streams, item group and item descriptions."""
    # bug_compat = spead2.BUG_COMPAT_PYSPEAD_0_5_2
    bug_compat = 0

    # From JSON File
    # lower = config['memory_pool']['lower']
    # upper = config['memory_pool']['upper']
    # max_free = config['memory_pool']['max_free']
    # initial = config['memory_pool']['initial']

    # This is not a JSON, therefore no need for parsing.
    # It is a dictionary, which just happens to have keys which are
    # byte strings. So simply use byte string to access the values
    upper = int(config[b'memory_pool:upper'])
    lower = int(config[b'memory_pool:lower'])
    max_free = int(config[b'memory_pool:max_free'])
    initial = int(config[b'memory_pool:initial'])
    stream = config[b'stream']
    stream_decode = stream.decode('utf-8')
    num_streams = ast.literal_eval(stream_decode)

    streams = []
    #for stream in config['streams']:
    for stream in num_streams:
        port = int(num_streams.get("port"))
        # port = redis_api.hget_variable("stream", stream.decode('utf-8'))
        log.debug('Creating stream on port {}'.format(port))
        s = spead2.recv.Stream(spead2.ThreadPool(), bug_compat)
        pool = spead2.MemoryPool(lower, upper, max_free, initial)
        s.set_memory_allocator(pool)
        # s.add_udp_reader(stream['port'])
        s.add_udp_reader(port)
        streams.append(s)
    return streams


def _pickle_write(filename, data):
    with open(filename, 'ab') as f:
        pickle.dump(data, f, protocol=2)


def _receive_heaps(config, streams, log):
    ms = {}

    ingest_proc = VisIngestProcessing(log)
    for stream in streams:
        item_group = spead2.ItemGroup()

        # Loop over all heaps in the stream.
        for heap in stream:
            log.info("Received heap {}".format(heap.cnt))

            # Statistics about the stream
            # stats = stream.stats
            # log.info('No.of heaps put in the stream {}'.format(stats.heaps))
            # log.info('Incomplete Heaps Evicted{}'.format(stats.incomplete_heaps_evicted))
            # log.info('Worked Blocked'.format(stats.worker_blocked))

            # Extract data from the heap into a dictionary.
            data = {}
            items = item_group.update(heap)
            for item in items.values():
                data[item.name] = item.value

            # Skip if the heap does not contain visibilities.
            if 'correlator_output_data' not in data:
                continue

            # Get data dimensions.
            time_index = heap.cnt - 2  # Extra -1 because first heap is empty.
            start_channel = data['visibility_channel_id'][0]
            num_channels = data['visibility_channel_count'][0]
            # max_times_per_file = config['output']['max_times_per_file']
            max_times_per_file = int(config[b'output:max_times_per_file'])
            # max_times_per_file = redis_api.get_variable("output:max_times_per_file")

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

            # Placeholders for further processing the data
            # Calculate data weights
            ingest_proc.data_weight()

            # Flag visibility data
            ingest_proc.flag_vis_data()

            # Demix visibility data
            ingest_proc.demix_vis_data()

            # Averaging visibility data
            ingest_proc.avg_vis_data()

            # Write visibility data.
            _pickle_write('/home/sdp/output/' + base_name + '.p', data)

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
    # log.info('Loading config: {}'.format(args.config_file.name))
    # config = json.load(args.config_file)
    log.info('Loading config from Redis Database')
    redis_api = RedisDatabase(args.host, args.port)
    # if args.print_settings:
    #     log.debug('Settings:\n {}'.format(json.dumps(config, indent=4,
    #                                                 sort_keys=True)))

    # Create streams and receive data.
    log.info('Creating streams...')
    config = _get_config(redis_api, log)
    streams = _create_streams(config, log)
    log.info('Waiting to receive...')
    _receive_heaps(config, streams, log)

    log.info('Done.')

if __name__ == '__main__':
    main()
