# -*- coding: utf-8 -*-
"""Tango Processing Controller Device server."""
from tango.server import run

from sip_logging import init_logger
from subarray_device import SubarrayDevice


def main(args=None, **kwargs):
    """Start the subarray device server."""
    return run([SubarrayDevice], args=args, **kwargs)


if __name__ == '__main__':
    init_logger()
    main()
