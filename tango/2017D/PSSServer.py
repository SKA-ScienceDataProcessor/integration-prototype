from tango.server import Device, DeviceMeta, attribute, command

class PSSDevice(Device, metaclass=DeviceMeta):

     def init_device(self):
        self.debug_stream('In PSS device init')

     @attribute
     def test(self):
         self.debug_stream("in test")
         return("testing")

if __name__ == "__main__":
     PSSDevice.run_server()
