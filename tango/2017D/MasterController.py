from tango.server import Device, DeviceMeta, attribute, command, run
from tango import Database, DbDevInfo
from subprocess import Popen

class MasterController(Device, metaclass=DeviceMeta):
    def init_device(self):
        self.debug_stream("MasterController starting")

    def init_device(self):
        self.debug_stream("Tango init")

    def _createPss(self):
        # A reference to the database
        db = Database()
       
        devices = db.get_server_list("PSS*").value_string
        for i in range(5):
           device = "PSSDevice/device" + str(i)
           if device in devices:
               self.debug_stream("Device " + device + " exists in Database")
           else:
           # The device we want to create
               new_device = "mid_SDP/LMC/PSS_00" + str(i)

               new_device_info = DbDevInfo()
               new_device_info._class="PSSDevice"
               new_device_info.server = "PSSDevice/device" + str(i)
               new_device_info.name = new_device

            # Add device
               self.debug_stream("Creating device: %s"% new_device)
               db.add_device(new_device_info)
           self.debug_stream("Starting device " + device)
           Popen(['python3','PSSServer.py','device' + str(i),'-v'])

    @command
    def test(self):
         self._createPss()
        

if __name__ == "__main__":
     MasterController.run_server()
