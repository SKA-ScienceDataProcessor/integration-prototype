# -*- coding: utf-8 -*-
"""Module main to stream SPEAD visibility data."""
import argparse
import json
import logging
import sys

from .heap_streamer import HeapStreamer
from .simulator import SimpleSimulator


def _init_log(level=logging.DEBUG):
    """Initialise the logging object.

    Args:
        level (int): Logging level.

    Returns:
        Logger: Python logging object.
    """
    log = logging.getLogger(__file__)
    log.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s: %(message)s',
                                  '%Y/%m/%d-%H:%M:%S')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


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


def main(config):
    """Main script function"""
    # Create simulation object, and start streaming SPEAD heaps
    sim = SimpleSimulator(config)
    sim.simulate_heaps(HeapStreamer(config, sim.frame_shape))


if __name__ == '__main__':
    # Parse command line arguments
    ARGS = _parse_command_line()

    # Load configuration.
    LOG = _init_log(level=logging.DEBUG if ARGS.verbose else logging.INFO)
    LOG.info('Loading config: %s', ARGS.config_file.name)
    CONFIG = json.load(ARGS.config_file)
    if ARGS.print_settings:
        LOG.debug('Settings:\n %s', json.dumps(CONFIG, indent=4,
                                               sort_keys=True))

    main(CONFIG)
