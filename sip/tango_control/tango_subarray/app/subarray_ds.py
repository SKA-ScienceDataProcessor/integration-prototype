#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tango Subarray Device server."""
import sys

from tango.server import run

from register_devices import register_subarray_devices
from sip_logging import init_logger
from subarray_device import SubarrayDevice
from release import LOG


def main(args=None, **kwargs):
    """Start the subarray device server."""
    LOG.info('Starting SDP Subarray devices.')
    return run([SubarrayDevice], verbose=True, msg_stream=sys.stdout,
               args=args, **kwargs)


if __name__ == '__main__':
    init_logger(logger_name='', show_log_origin=True)
    init_logger(show_log_origin=True)
    register_subarray_devices()
    main()
