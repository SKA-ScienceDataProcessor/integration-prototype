#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SIP SDP Tango Logger Device server.

Run with:

```bash
python3 sdp_logger_ds.py 1 -v4
```
"""
import sys

from tango import Database, DbDevInfo
from tango.server import run

from sip_logging import init_logger
from sdp_logger_device import SDPLoggerDevice

from release import LOG, __service_id__


def register_logger():
    """Register the SDP Logger device."""
    tango_db = Database()
    device = "sip_sdp/elt/logger"
    device_info = DbDevInfo()
    device_info._class = "SDPLoggerDevice"
    device_info.server = "sdp_logger_ds/1"
    device_info.name = device
    devices = tango_db.get_device_name(device_info.server, device_info._class)
    if device not in devices:
        LOG.info('Registering device "%s" with device server "%s"',
                 device_info.name, device_info.server)
        tango_db.add_device(device_info)


def main(args=None, **kwargs):
    """Run the Tango SDP Logger device server."""
    LOG.info('Starting %s', __service_id__)
    return run([SDPLoggerDevice], verbose=True, args=args,
               msg_stream=sys.stdout, **kwargs)


if __name__ == '__main__':

    init_logger(logger_name='', show_log_origin=True)
    init_logger(show_log_origin=True)
    register_logger()
    main()
