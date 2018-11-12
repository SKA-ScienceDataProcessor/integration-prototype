#!/usr/bin/python3
"""Register the SDP Subarray devices with the TANGO Database."""
import logging
import os
import sys

from tango import Database, DbDevInfo, DeviceProxy


def init_logger():
    """Initialise the logger."""
    # Attach stdout StreamHandler to the 'sip' logger. This will apply
    # to all logger objects with a name prefixed with 'sip.'
    log = logging.getLogger('sip')
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = os.getenv('SIP_LOG_FORMAT', '%(asctime)s.%(msecs)03d | '
                    '%(name)s | %(levelname)-7s | %(message)s')
    handler.setFormatter(logging.Formatter(fmt, '%Y-%m-%dT%H:%M:%S'))
    log.addHandler(handler)
    log.setLevel(os.getenv('SIP_LOG_LEVEL', 'DEBUG'))


def register_subarray_devices():
    """Register subarray devices."""
    db = Database()
    log = logging.getLogger('sip.tango_control.subarray')
    device_info = DbDevInfo()
    device_info._class = "SubarrayDevice"
    device_info.server = "SubarrayDS/1"

    for index in range(16):
        device_info.name = "sdp/elt/subarray_{:02d}".format(index)
        log.info("Creating TANGO device: %s", device_info.name)
        db.add_device(device_info)

    db.put_class_property(device_info._class, dict(version='1.0.0'))


if __name__ == '__main__':
    init_logger()
    register_subarray_devices()
