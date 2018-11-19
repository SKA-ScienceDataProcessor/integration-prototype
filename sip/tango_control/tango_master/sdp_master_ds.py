#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIP SDP Tango Master Device server.

Run with:

```bash
python3 sdp_master_ds.py 1 -v4
```
"""
from sip_logging import init_logger

from tango.server import run

from sdp_master_device import SDPMasterDevice


def main(args=None, **kwargs):
    """Run the Tango SDP Master device server."""
    init_logger()
    return run([SDPMasterDevice], args=args, **kwargs)


if __name__ == '__main__':
    main()
