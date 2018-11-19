# -*- coding: utf-8 -*-
"""Tango Processing Controller Device server."""
from sip_logging import init_logger

from tango.server import run

from subarray_device import SubarrayDevice


def main(args=None, **kwargs):
    """Start the subarray device server."""
    return run([SubarrayDevice], args=args, **kwargs)


if __name__ == '__main__':
    init_logger()
    main()
