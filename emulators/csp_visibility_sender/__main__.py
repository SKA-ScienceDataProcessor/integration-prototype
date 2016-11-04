# -*- coding: utf-8 -*-
"""Module main to stream SPEAD visibility data."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import logging
import argparse
import simplejson as json
from emulators.csp_visibility_sender.heap_streamer import HeapStreamer
from emulators.csp_visibility_sender.simulator import Simulator


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
    sim = Simulator(config, log)

    # Create streamer
    sim.simulate_heaps(HeapStreamer(config, sim.frame_shape, log))

if __name__ == '__main__':
    main()
