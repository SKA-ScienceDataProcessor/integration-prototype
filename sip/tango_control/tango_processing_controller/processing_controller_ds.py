# -*- coding: utf-8 -*-
"""Tango Processing Controller Device server."""
from tango.server import run

from processing_block_device import ProcessingBlockDevice


def main(args=None, **kwargs):
    """Start the Processing Controller device server."""
    return run([ProcessingBlockDevice], args=args, **kwargs)


if __name__ == '__main__':
    main()
