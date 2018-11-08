#!/usr/bin/python3

from PyTango import Database, DbDevInfo

# A reference to the database

db = Database()

dev_info1 = DbDevInfo()
dev_info1.name = 'sdp/ProcessingBlock/test'
dev_info1._class = 'ProcessingBlockDevice'
dev_info1.server = 'ProcessingControllerDS/test'
db.add_server(dev_info1.server, dev_info1, with_dserver=True)
