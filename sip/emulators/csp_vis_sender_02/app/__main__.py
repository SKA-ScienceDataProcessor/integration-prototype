# -*- coding: utf-8 -*-
"""Module main to stream SPEAD visibility data."""
import sys

import argparse
import logging
import json

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
        prog='csp_visibility_sender',
        description='Send fake visibility data using the SPEAD protocol.')
    parser.add_argument('config_file', type=argparse.FileType('r'),
                        help='JSON configuration file.')
    parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                        action='store_true')
    parser.add_argument('-p', '--print_settings', help='Print settings file.',
                        action='store_true')
    return parser.parse_args()


def main(config, log):
    """Main script function"""
    # Create simulation object, and start streaming SPEAD heaps
    sim = SimpleSimulator(config, log)
    sim.simulate_heaps()


if __name__ == '__main__':
    # Parse command line arguments
    args = _parse_command_line()

    # Initialise logging.
    _log = _init_log(level=logging.DEBUG if args.verbose else logging.INFO)

    # Load configuration.
    _log.info('Loading config: {}'.format(args.config_file.name))
    _config = json.load(args.config_file)
    if args.print_settings:
        _log.debug('Settings:\n {}'.format(json.dumps(_config, indent=4,
                                                      sort_keys=True)))

    main(_config, _log)
