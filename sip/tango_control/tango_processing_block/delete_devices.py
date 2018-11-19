#!/usr/bin/python3
"""Delete Processing Block devices from the TANGO Database."""
import logging
import argparse

from sip_logging import init_logger
from tango import Database


def delete_pb_devices():
    """Delete PBs devices from the Tango database."""
    parser = argparse.ArgumentParser(description='Register PB devices.')
    parser.add_argument('num_pb', type=int,
                        help='Number of PBs devices to register.')
    args = parser.parse_args()

    log = logging.getLogger('sip.tango_control.subarray')
    tango_db = Database()
    log.info("Deleting PB devices:")
    for index in range(args.num_pb):
        name = 'sip_sdp/pb/{:05d}'.format(index)
        log.info("\t%s", name)
        tango_db.delete_device(name)


if __name__ == '__main__':
    init_logger()
    delete_pb_devices()
