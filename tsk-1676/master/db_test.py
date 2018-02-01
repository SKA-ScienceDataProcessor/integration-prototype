from tango import Database, DbDevInfo

#  A reference on the DataBase
db = Database()

# The 3 devices name we want to create
# Note: these 3 devices will be served by the same DServer
new_device_name1 = "px1/tdl/mouse1"
new_device_name2 = "px1/tdl/mouse2"
new_device_name3 = "px1/tdl/mouse3"

# Define the Tango Class served by this  DServer
new_device_info_mouse = DbDevInfo()
new_device_info_mouse._class = "Mouse"
new_device_info_mouse.server = "ds_Mouse/server_mouse"

# add the first device
print("Creating device: %s" % new_device_name1)
new_device_info_mouse.name = new_device_name1
db.add_device(new_device_info_mouse)

# add the next device
print("Creating device: %s" % new_device_name2)
new_device_info_mouse.name = new_device_name2
db.add_device(new_device_info_mouse)

# add the third device
print("Creating device: %s" % new_device_name3)
new_device_info_mouse.name = new_device_name3
db.add_device(new_device_info_mouse)
