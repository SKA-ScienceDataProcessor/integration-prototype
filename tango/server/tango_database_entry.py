#! /usr/bin/python
#
# The Tango database device can be created programatically (as shown here)
# or using the graphical JAVA-based tool - jive

import PyTango

dev_info = PyTango.DbDevInfo()
dev_info.server = "MasterController/mc"
dev_info._class = "MasterController"
dev_info.name = "ska/sdp/mc"

db = PyTango.Database()
db.add_device(dev_info)

