#! /usr/bin/python3

import PyTango
db = PyTango.Database()
print('Connected to Tango Database OK!!!!!!')
print('Now to list defined Device Servers....')
print(db.get_server_list())

