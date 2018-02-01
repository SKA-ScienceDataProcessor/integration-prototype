from tango import Database, DbDevInfo
#
# Create MasterController Tango database entry
#
# A reference to the database
db = Database()

# The devices we want to create
new_device = "mid_SDP/elt/telmodel"

new_device_info = DbDevInfo()
new_device_info._class="SDPMasterController"
new_device_info.server = "SDPMasterController/device"
new_device_info.name = new_device

# Add device
print("Creating device: %s"% new_device)
db.add_device(new_device_info)

