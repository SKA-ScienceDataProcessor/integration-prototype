#!/usr/bin/env python3
"""Register the SDP Master Device with the TANGO Database."""
from tango import Database, DbDevInfo


def register_master():
    """Register the SDP Master device."""
    tango_db = Database()
    # <domain>/<family>/<member>
    device = "sip_sdp/elt/master"

    # if tango_db.get_device_member(device).value_string:
    #     print("Device " + device + " exists in Database")
    # else:
    print("Creating device: ", device)
    new_device_info = DbDevInfo()
    # pylint: disable=protected-access
    new_device_info._class = "SDPMasterDevice"
    new_device_info.server = "sdp_master_ds/1"
    new_device_info.name = device
    tango_db.add_device(new_device_info)


if __name__ == '__main__':
    register_master()
