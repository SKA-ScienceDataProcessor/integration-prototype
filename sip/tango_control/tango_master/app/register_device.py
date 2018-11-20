#!/usr/bin/env python3
"""Register the SDP Master Device with the TANGO Database."""
from tango import Database, DbDevInfo
from sip_logging import init_logger

from release import LOG


def register_master():
    """Register the SDP Master device."""
    tango_db = Database()
    device = "sip_sdp/elt/master"
    device_info = DbDevInfo()
    device_info._class = "SDPMasterDevice"
    device_info.server = "sdp_master_ds/1"
    device_info.name = device
    LOG.info('Registering device "%s" with device server "%s"',
             device_info.name, device_info.server)
    tango_db.add_device(device_info)


if __name__ == '__main__':
    init_logger()
    register_master()
