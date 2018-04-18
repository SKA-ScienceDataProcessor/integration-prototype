# -*- coding: utf-8 -*-
"""Python script to register device"""
from tango import Database, DbDevInfo

# Define the tango Class served by this DServer
device_info = DbDevInfo()
device_info.server = 'Test/TestServer'
device_info._class = 'Test'
device_info.name = 'sip_SDP/elt/test'

print('Creating device: %s' % device_info.name)
db = Database()
db.add_device(device_info)
