# -*- coding: utf-8 -*-
"""SIP SDP Tango Master Device server."""
from tango.server import run

from SDPMasterDevice import SDPMasterDevice


def main(args=None, **kwargs):
    """Main function."""
    return run((SDPMasterDevice,), args=args, **kwargs)


if __name__ == '__main__':
    main()
