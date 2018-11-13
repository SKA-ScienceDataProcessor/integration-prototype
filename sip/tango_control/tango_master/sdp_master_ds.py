# -*- coding: utf-8 -*-
"""SIP SDP Tango Master Device server."""
from tango.server import run

from sdp_master import SDPMasterDevice
from sip_logging import init_logger


def main(args=None, **kwargs):
    """Run the Tango SDP Master device server."""
    init_logger()
    return run([SDPMasterDevice], args=args, **kwargs)


if __name__ == '__main__':
    main()
