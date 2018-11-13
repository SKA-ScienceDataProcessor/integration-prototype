#!/usr/bin/env python3
"""Register the SDP Subarray devices with the TANGO Database."""
import logging

from tango import Database, DbDevInfo

from sip_logging import init_logger


def register_subarray_devices():
    """Register subarray devices."""
    tango_db = Database()
    log = logging.getLogger('sip.tango_control.subarray')
    log.info("Registering Subarray devices:")
    device_info = DbDevInfo()
    # pylint: disable=protected-access
    device_info._class = "SubarrayDevice"
    device_info.server = "subarray_ds/1"

    for index in range(16):
        device_info.name = "sdp/elt/subarray_{:02d}".format(index)
        log.info("\t%s", device_info.name)
        tango_db.add_device(device_info)

    tango_db.put_class_property(device_info._class, dict(version='1.0.0'))


if __name__ == '__main__':
    init_logger()
    register_subarray_devices()
