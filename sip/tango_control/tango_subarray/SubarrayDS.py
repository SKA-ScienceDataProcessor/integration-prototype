# -*- coding: utf-8 -*-
"""Tango Processing Controller Device server."""
from tango.server import run
from subarray_device import SubarrayDevice


def main(args=None, **kwargs):
    """Main function."""
    return run([SubarrayDevice], args=args, **kwargs)


if __name__ == '__main__':
    main()
