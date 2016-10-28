# -*- coding: utf-8 -*-
"""CSP visibility data emulator.

Issues/TODO:
    - Integrate documentation in this module with sphinx
    - Need better way of configuration of what data is to be sent.
    - Need to investigate exactly what data items need to be sent.
        - Visibility amplitudes (+ coords?)
    - look at SPEAD2 optimisation guidelines
    - Look into non-blocking sends?

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


# Heap item description according to ICD 100-000000-002 and 300-000000-002_01
# Note: User ItemIdentifier space starts at 0x0016.
__heap__ = [
    # Per SPEAD heap
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
        "format": [('u', 8)]
    },
    {
        "id": 0x0051,
        "name": "complex_visibility",
        "description": "SDP_REQ_INT-51",
        "format": [('f', 32), ('f', 32)]
    },
    # {
    #     "id": 0x0022,
    #     "name": "complex_visibility_p0",
    #     "description": "SDP_REQ_INT-51",
    #     "format": [('f', 32), ('f', 32)]
    # },
    # {
    #     "id": 0x0023,
    #     "name": "complex_visibility_p1",
    #     "description": "SDP_REQ_INT-51",
    #     "format": [('f', 32), ('f', 32)]
    # },
    # {
    #     "id": 0x0024,
    #     "name": "complex_visibility_p2",
    #     "description": "SDP_REQ_INT-51",
    #     "format": [('f', 32), ('f', 32)]
    # },
    # {
    #     "id": 0x0025,
    #     "name": "complex_visibility_p3",
    #     "description": "SDP_REQ_INT-51",
    #     "format": [('f', 32), ('f', 32)]
    # },
    {
        "id": 0x0052,
        "name": "flagging_fraction",
        "description": "SDP_REQ_INT-52",
        "format": [('u', 8)]
    },

]


class Simulation(object):
    """Simulation class"""

    def __init__(self, config, log):
        """Constructor"""
        _obs = config['observation']
        _sim = _obs['simulation']
        self.log = log
        self.config = config
        self.num_baselines = _sim['num_baselines']
        self.num_frames = _obs['num_times']
        self.num_channels = config['observation']['num_channels'] // \
                            len(config['sender_node']['streams'])
        self.frame_shape = (1, 1, self.num_channels, self.num_baselines, 4)

        self.log.debug('Number of channels per heap = {}'.
                       format(self.num_channels))
        self.log.debug('Number of baselines = {}'.format(self.num_baselines))
        self.payload = {
            'timestamp_utc': [(0, 0)],
            'channel_baseline_id': [(0, 0)],
            'channel_baseline_count': [(0, 0)],
            'schedule_block': [0],
            'hardware_source_id': [0],
            'complex_visibility': np.zeros(self.frame_shape)
            # 'complex_visibility_p0': np.zeros(self.frame_shape),
            # 'complex_visibility_p1': np.zeros(self.frame_shape),
            # 'complex_visibility_p2': np.zeros(self.frame_shape),
            # 'complex_visibility_p3': np.zeros(self.frame_shape)
        }

    def get_heap(self, frame_id):
        """Generate the payload data for the frame."""
        t = frame_id
        self.payload['timestamp_utc'] = [(t, t + 1)]
        self.payload['complex_visibility'] = np.ones(self.frame_shape) * t
        self.payload['time_centroid_index'] = np.ones(self.frame_shape,
                                                      dtype=np.uint8)
        self.payload['flagging_fraction'] = np.ones(self.frame_shape,
                                                    dtype=np.uint8)
        # self.payload['complex_visibility_p0'] = np.ones(self.frame_shape) * t
        # self.payload['complex_visibility_p1'] = np.ones(self.frame_shape) * t
        # self.payload['complex_visibility_p2'] = np.ones(self.frame_shape) * t
        # self.payload['complex_visibility_p3'] = np.ones(self.frame_shape) * t
        return self.payload


def _get_heap_size():
    heap_size = 0
    for item in __heap__:
        num_elements = sum(size for size in item['shape'])
        if 'type' in item:
            heap_size += np.dtype(item['type']).itemsize * num_elements
        elif 'format' in item:
            item_bits = sum(bits for _, bits in item['format'])
            heap_size += item_bits // 8 * num_elements
    return heap_size


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
        description='Send fake visibility data using the SPEAD protocol.')
    parser.add_argument('config_file', type=argparse.FileType('r'),
                        help='JSON configuration file..')
    parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                        action='store_true')
    parser.add_argument('-p', '--print_settings', help='Print settings file.',
                        action='store_true')
    return parser.parse_args()


def _create_streams(config, log):
    """Construct streams, item group and item descriptions."""
    # Construct the SPEAD flavour description
    # Flavour(version, item_pointer_bits, heap_address_bits, bug_compat_mask)
    version = config['spead_flavour']['version']
    item_pointer_bits = config['spead_flavour']['item_pointer_bits']
    heap_address_bits = config['spead_flavour']['heap_address_bits']
    bug_compat_mask = config['spead_flavour']['bug_compat_mask']
    flavour = spead2.Flavour(version, item_pointer_bits, heap_address_bits,
                             bug_compat_mask)

    # Create a thread pool of 1 thread used to send packets

    # Construct a UDP stream object for a blocking send.
    streams = list()
    for i, stream in enumerate(config['sender_node']['streams']):
        # Create ItemGroup & HeapGenerator associated with the item group.
        host = stream['host']
        port = stream['port']
        rate = stream['rate'] if 'rate' in stream else 0
        threads = stream['threads'] if 'threads' in stream else 1

        log.debug('Configuring stream {}:'.format(i))
        log.debug('  Address = {}:{}'.format(host, port))
        log.debug('  Flavour = SPEAD-{}-{} v{} compat:{}'.
                  format(flavour.item_pointer_bits, flavour.heap_address_bits,
                         flavour.version, flavour.bug_compat))
        log.debug('  Threads = {}'.format(threads))
        log.debug('  Rate    = {}'.format(rate))
        stream_config = spead2.send.StreamConfig(rate=rate)

        thread_pool = spead2.ThreadPool(threads=threads)
        stream = spead2.send.UdpStream(thread_pool, host, port, stream_config)
        item_group = spead2.send.ItemGroup(flavour=flavour)
        streams.append((stream, item_group))

        for j, item in enumerate(__heap__):
            item_id = item['id']
            if isinstance(item_id, str):
                item_id = int(item_id, 0)
            name = item['name']
            desc = item['description']
            item_type = item['type'] if 'type' in item else None
            item_format = item['format'] if 'format' in item else None
            shape = item['shape']
            log.debug('Adding item {} : {} {}'.format(j, item_id, name))
            log.debug('  description = {}'.format(desc))
            if item_type is not None:
                log.debug('  type = {}'.format(item_type))
            if item_format is not None:
                log.debug('  format = {}'.format(item_format))
            log.debug('  shape = {}'.format(shape))
            item_group.add_item(item_id, name, desc, shape=shape,
                                dtype=item_type, format=item_format)
    return streams


def _send_blocks(config, streams, log, sim):
    """Send the data."""
    log.info('Sending data ...')
    t0 = time.time()
    num_heaps = config['observation']['num_times']

    # Send start-of-stream marker for each stream
    for stream, item_group in streams:
        stream.send_heap(item_group.get_start())

    # Send main data payload for each stream.
    for i in range(num_heaps):
        log.debug('  heap {:03d}/{:03d}'.format(i, num_heaps))
        _payload = sim.get_heap(i)
        for stream, item_group in streams:
            for name, item in item_group.items():
                log.debug('    item: 0x{:04X} {}'.format(item.id, name))
                item.value = _payload[name]

            # Send the updated heap
            _heap = item_group.get_heap()
            stream.send_heap(_heap)

    # Send a end-of-stream marker for each stream
    for stream, item_group in streams:
        stream.send_heap(item_group.get_end())

    heap_size = _get_heap_size()
    total_bytes = heap_size * num_heaps
    total_time = time.time() - t0
    log.info('Sending complete in {} s'.format(total_time))
    log.info('Total bytes = {} ({:.3f} MiB)'.
              format(total_bytes, total_bytes / 1024**2))
    log.info('Rate = {:.3f} MiB/s'
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

    # Create simulation object
    sim = Simulation(config, log)

    # Set the shape of the visibility data item.
    for item in __heap__:
        if 'complex_visibility' in item['name']:
            item['shape'] = sim.frame_shape
        if item['name'] == 'time_centroid_index':
            item['shape'] = sim.frame_shape
        if item['name'] == 'flagging_fraction':
            item['shape'] = sim.frame_shape

    # Create streams for sending data.
    streams = _create_streams(config, log)

    # Send blocks of data
    _send_blocks(config, streams, log, sim)

if __name__ == '__main__':
    main()
