#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tango Processing Controller Device server."""
import sys

from tango.server import run

from processing_block_device import ProcessingBlockDevice
from sip_logging import init_logger
from register_devices import register_pb_devices
from release import LOG


def main(args=None, **kwargs):
    """Start the Processing Block device server."""
    LOG.info('Starting SDP PB devices.')
    return run([ProcessingBlockDevice], verbose=True, msg_stream=sys.stdout,
               args=args, **kwargs)


if __name__ == '__main__':
    init_logger(logger_name='', show_log_origin=True)
    init_logger(show_log_origin=True)
    register_pb_devices(100)
    main()
