# -*- coding: utf-8 -*-
"""Tango Processing Controller Device server."""
from tango.server import run

from ProcessingBlockDevice import ProcessingBlockDevice


def main(args=None, **kwargs):
    """Main function."""
    return run((ProcessingBlockDevice,), args=args, **kwargs)


if __name__ == '__main__':
    main()
