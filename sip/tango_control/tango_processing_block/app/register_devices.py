#!/usr/bin/env python3
"""Register Processing Block devices with the TANGO Database."""
import argparse

from tango import Database, DbDevInfo

from sip_logging import init_logger
from .release import LOG


def parse_command_args():
    """Command line parser."""
    parser = argparse.ArgumentParser(description='Register PB devices.')
    parser.add_argument('num_pb', type=int,
                        help='Number of PBs devices to register.')
    return parser.parse_args()


def register_pb_devices(num_pbs: int = 100):
    """Register PBs devices.

    Note(BMo): Ideally we do not want to register any devices here. There
    does not seem to be a way to create a device server with no registered
    devices in Tango. This is (probably) because Tango devices must have been
    registered before the server starts ...
    """
    tango_db = Database()
    LOG.info("Registering PB devices:")
    dev_info = DbDevInfo()
    # pylint: disable=protected-access
    dev_info._class = 'ProcessingBlockDevice'
    dev_info.server = 'processing_block_ds/1'

    for index in range(num_pbs):
        dev_info.name = 'sip_sdp/pb/{:05d}'.format(index)
        LOG.info("\t%s", dev_info.name)
        tango_db.add_device(dev_info)


if __name__ == '__main__':
    init_logger()
    args = parse_command_args()
    register_pb_devices(args.num_pbs)
