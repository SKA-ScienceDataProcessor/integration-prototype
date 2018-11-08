#!/usr/bin/python3

from PyTango import Database, DbDevInfo

# A reference to the database

db = Database()

device = "sdp/elt/master"
if db.get_device_member(device).value_string:
    print("Device " + device + " exists in Database")
else:
    # The device we want to create
    new_device = device

    new_device_info = DbDevInfo()
    new_device_info._class = "MasterController"
    new_device_info.server = "MasterController/mcont"
    new_device_info.name = new_device

    # Add device
    print("Creating device: ",new_device)
    db.add_device(new_device_info)
