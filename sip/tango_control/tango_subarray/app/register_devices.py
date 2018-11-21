#!/usr/bin/env python3
"""Register the SDP Subarray devices with the TANGO Database."""
from release import LOG
from sip_logging import init_logger

from tango import Database, DbDevInfo


def register_subarray_devices():
    """Register subarray devices."""
    tango_db = Database()
    LOG.info("Registering Subarray devices:")
    device_info = DbDevInfo()
    # pylint: disable=protected-access
    device_info._class = "SubarrayDevice"
    device_info.server = "subarray_ds/1"

    for index in range(16):
        device_info.name = "sip_sdp/elt/subarray_{:02d}".format(index)
        LOG.info("\t%s", device_info.name)
        tango_db.add_device(device_info)

    tango_db.put_class_property(device_info._class, dict(version='1.0.0'))


if __name__ == '__main__':
    init_logger()
    register_subarray_devices()
