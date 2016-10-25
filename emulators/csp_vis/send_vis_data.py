# -*- coding: utf-8 -*-
"""Test code for sending visibility data using SPEAD.

Issues/TODO:
    - Integrate documentation in this module with sphinx
    - Need better way of configuration of what data is to be sent.
    - Need to investigate exactly what data items need to be sent.
        - Visibility amplitudes (+ coords?)
    - look at SPEAD2 optimisation guidelines
    - Look into non-blocking sends?
    - Currently python2.7 code need to look at making this python3?

References:
    - ICD documents:
      https://confluence.ska-sdp.org/pages/viewpage.action?pageId=145653762
    - spead2 library code
      https://github.com/ska-sa/spead2
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import spead2
import spead2.send
import sys
import logging
import numpy as np
import time
import argparse
import simplejson as json


def _init_log(level=logging.DEBUG, log_file=None):
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
        description='Send fake visibility data using the SPEAD protocol.')
    parser.add_argument('config_file', type=argparse.FileType('r'),
                        help='JSON configuration file.')
    parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                        action='store_true')
    parser.add_argument('-p', '--print_settings', help='Print settings file.',
                        action='store_true')

    return parser.parse_args()


def _create_streams(config, log):
    """Construct streams, item group and item descriptions."""
    # Construct the SPEAD flavour description
    # Flavour(version, item_pointer_bits, heap_address_bits, bug_compat_mask)
    version = config['flavour']['version']
    item_pointer_bits = config['flavour']['item_pointer_bits']
    heap_address_bits = config['flavour']['heap_address_bits']
    bug_compat_mask = config['flavour']['bug_compat_mask']
    flavour = spead2.Flavour(version, item_pointer_bits, heap_address_bits,
                             bug_compat_mask)

    item_group = spead2.send.ItemGroup(flavour=flavour)

    # Create a thread pool of 1 thread used to send packets
    thread_pool = spead2.ThreadPool(threads=1, affinity=[])
    # Construct a UDP stream object for a blocking send.
    streams = list()
    for i, stream in enumerate(config['streams']):
        # Create ItemGroup & HeapGenerator associated with the item group.
        host = stream['host']
        port = stream['port']
        rate = stream['rate']
        log.debug('Configuring stream {}:'.format(i))
        log.debug('  Address = {}:{}'.format(host, port))
        log.debug('  Flavour = SPEAD-{}-{} v{} compat:{}'.
                  format(flavour.item_pointer_bits, flavour.heap_address_bits,
                         flavour.version, flavour.bug_compat))
        log.debug('  Rate    = {}'.format(rate))
        stream_config = spead2.send.StreamConfig(rate=rate)
        streams.append((spead2.send.UdpStream(thread_pool, host, port,
                                              stream_config), item_group))
        for j, item in enumerate(stream["items"]):
            id = int(item['id'], 0)
            name, desc = item['name'], item['description']
            shape, type = tuple(item['shape']), item['type']
            log.debug('Adding item {}'.format(j))
            log.debug('  id = 0x{:02X}'.format(id))
            log.debug('  name = {}'.format(name))
            log.debug('  description = {}'.format(desc))
            log.debug('  shape = {}'.format(shape))
            log.debug('  type = {}'.format(type))
            item_group.add_item(id, name, desc, shape=shape, dtype=type)
    del thread_pool
    return streams


def _send_blocks(config, streams, log):
    """Send the data."""
    log.info('Sending data ...')
    t0 = time.time()
    num_blocks = config['payload']['num_blocks']
    total_bytes = 0

    # Send start-of-stream marker (FIXME(BM) needed?)
    for stream_ in streams:
        ig = stream_[1]
        stream = stream_[0]
        stream.send_heap(ig.get_start())

    # Send main data payload.
    for b in range(num_blocks):
        for stream_ in streams:
            ig = stream_[1]
            stream = stream_[0]
            for item in ig.items():
                log.debug('  block {:03d}/{:03d}: {}'.
                          format(b, num_blocks, item[0]))
                item[1].value = np.ones(item[1].shape, item[1].dtype) * b
                total_bytes += item[1].dtype.itemsize * item[1].value.size

            # Return a new heap which contains all of the new items and item
            # descriptors since the last call.
            new_heap = ig.get_heap()
            # Blocking send.
            stream.send_heap(new_heap)

    # Send a heap that contains only an end-of-stream marker.
    stream.send_heap(ig.get_end())

    total_time = time.time() - t0
    log.info('Sending complete in {} s'.format(total_time))
    log.debug('Total bytes = {} ({:.3f} MiB)'.
              format(total_bytes, total_bytes / 1024**2))
    log.debug('Rate = {:.3f} MiB/s'
              .format(total_bytes / (1024**2 * total_time)))


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

    # Create streams for sending data.
    streams = _create_streams(config, log)

    # Send blocks of data
    _send_blocks(config, streams, log)

if __name__ == '__main__':
    main()
