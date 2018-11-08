# -*- coding: utf-8 -*-
"""Python script to register device"""
from tango import Database, DbDevInfo

# http://pytango.readthedocs.io/en/stable/database.html

db = Database()

# Define the tango Class served by this DServer
device_info = DbDevInfo()
device_info.name = 'sip_SDP/test/1'
device_info._class = 'Test'
device_info.server = 'Test/test'
print('Adding device: %s' % device_info.name)

# NOTE: This also adds the server defined by device_info.server to the db
db.add_device(device_info)
