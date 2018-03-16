#
# Enter this device server into the Starter system on this node
#
# Example only - tailor as needed!
#
from tango import DeviceProxy, DevFailed, Database
import os

node = input('Enter node to start on : ')
try:
   starter = DeviceProxy('tango/admin/' + node)
except DevFailed as e:
   print('Tango error - ' + e.args[0].desc)
   quit()

start_dict = starter.get_property('StartDsPath')
key, value = start_dict.popitem()
if  len(value):
    print('Node starter directory path = ' + ''.join(value))
    dir = input('Enter new value to change: ')
else:
    dir = input('Node Starter directory: ')
if dir:
    starter.put_property({'StartDsPath' : dir}) 
    print('Value changed')

cls = input('Enter Device Controller class name: ')
db = Database()
sinfo = db.get_server_info(cls + '/device')
print('Current run level=' + str(sinfo.level))
level = input('Change run level? (0-5 or <CR>): ')
if level:
   sinfo.level = int(level)
   db.put_server_info(sinfo)
   print('Changed OK!')
yesno = input('Start server (y/n)? ')
if yesno.lower() == 'y':
   starter.DevStart(cls)
running = starter.read_attribute("RunningServers")
print("Servers running on {} = {}".format(node,running.value))
    
