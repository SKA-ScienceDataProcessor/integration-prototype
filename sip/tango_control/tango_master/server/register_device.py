#!/usr/bin/python3
"""Register the SDP Master Device with the TANGO Database."""
from tango import Database, DbDevInfo


def register_master():
    """Register the SDP Master device."""
    db = Database()
    # <domain>/<family>/<member>
    device = "sdp/elt/SDPMaster"

    if db.get_device_member(device).value_string:
        print("Device " + device + " exists in Database")
    else:
        print("Creating device: ", device)
        new_device_info = DbDevInfo()
        # Class of the device.
        new_device_info._class = "SDPMaster"
        # <Server name>/<instance name>
        new_device_info.server = "SDPMasterDS/sip"
        new_device_info.name = device
        db.add_device(new_device_info)


if __name__ == '__main__':
    register_master()
