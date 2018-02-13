# -*- coding: utf-8 -*-
"""Module main to stream SPEAD visibility data."""
import argparse
import json
import logging
import sys

from .heap_streamer import HeapStreamer
from .simulator import SimpleSimulator


def _init_log(level=logging.DEBUG):
    """Initialise logging.

    Args:
        level (int): Logging level.
    """
    log = logging.getLogger()
    log.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s: %(message)s',
                                  '%Y/%m/%d-%H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)


def _parse_command_line():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='csp_visibility_sender',
        description='Send fake visibility data using the SPEAD protocol.')
    parser.add_argument('config_file', type=argparse.FileType('r'),
                        help='JSON configuration file.')
    parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                        action='store_true')
    parser.add_argument('-p', '--print_settings', help='Print settings file.',
                        action='store_true')
    return parser.parse_args()


def main():
    """Main
    Create simulation object, and start streaming SPEAD heaps
    """
    args = _parse_command_line()
    _init_log(level=logging.DEBUG if args.verbose else logging.INFO)
    log = logging.getLogger()
    log.info('Loading config: %s', args.config_file.name)
    config = json.load(args.config_file)
    if args.print_settings:
        log.info('Settings:\n %s', json.dumps(config, indent=2, sort_keys=True))
    sim = SimpleSimulator(config)
    sim.simulate_heaps(HeapStreamer(config, sim.frame_shape))


if __name__ == '__main__':
    main()
