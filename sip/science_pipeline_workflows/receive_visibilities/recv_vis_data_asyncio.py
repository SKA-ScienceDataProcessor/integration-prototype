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
import spead2.recv.asyncio
import asyncio
import signal

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
    #streams = []
    for stream_data in config['streams']:
        log.debug('Creating stream on port {}'.format(stream_data['port']))

        #s = spead2.recv.Stream(spead2.ThreadPool(), bug_compat)

        # Async Receive
        stream = spead2.recv.asyncio.Stream(spead2.ThreadPool(), bug_compat)
        pool = spead2.MemoryPool(lower, upper, max_free, initial)
        stream.set_memory_allocator(pool)
        stream.add_udp_reader(stream_data['port'])
        # streams.append(s)
    return stream


def _pickle_write(filename, data):
    with open(filename, 'ab') as f:
        pickle.dump(data, f, protocol=2)


@asyncio.coroutine
def run_stream(stream, log):
    try:
        item_group = spead2.ItemGroup()
        num_heaps = 0
        while True:
            try:
                heap = yield from(stream.get())
                print("Received heap {} on stream".format(heap.cnt))
                desp = False
                write = True
                try:
                    if desp:
                        for raw_descriptor in heap.get_descriptors():
                            descriptor = spead2.Descriptor.from_raw(raw_descriptor, heap.flavour)
                            print('''\
    Descriptor for {0.name} ({0.id:#x})
      description: {0.description}
      format:      {0.format}
      dtype:       {0.dtype}
      shape:       {0.shape}'''.format(descriptor))
                    changed = item_group.update(heap)
                    data = {}

                    for (key, item) in changed.items():
                        if write:
                            print(key, '=', item.value)
                            data[item.name] = item.value

                        # Get data dimensions.
                        time_index = heap.cnt - 2  # Extra -1 because first heap is empty.

                        # max_times_per_file = config['output']['max_times_per_file']

                        # Construct filename.
                        base_name = 'vis_T'
                        data['time_index'] = time_index

                        # Write visibility data.
                        _pickle_write('/home/sdp/output/' + base_name + '.p', data)

                except ValueError as e:
                    print("Error raised processing heap: {}".format(e))

            except (spead2.Stopped, asyncio.CancelledError):
                print("Shutting down stream after {} heaps".format(num_heaps))
                stats = stream.stats
                for key in dir(stats):
                    if not key.startswith('_'):
                        print("{}: {}".format(key, getattr(stats, key)))
                break
    finally:
        stream.stop()


def make_coro(config,log):
    stream = _create_streams(config, log)
    log.info("Done with create streams")
    return run_stream(stream, log), stream


def stop_streams():
    for stream in streams:
        stream.stop()

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

    coros_and_streams = [make_coro(config,log)]
    coros, streams = zip(*coros_and_streams)
    main_task = asyncio.async(asyncio.gather(*coros))
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop_streams)
    try:
        loop.run_until_complete(main_task)
    except asyncio.CancelledError:
        pass
    loop.close()

if __name__ == '__main__':
    main()
