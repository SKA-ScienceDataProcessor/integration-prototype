#! /usr/bin/python3

from PyTango import DeviceProxy
import os
import threading
import time
from datetime import datetime
import tango
import pdb


# An example client for the MasterController


class HeartBeat(object):


    def __init__(self, deviceProxy):
       self.dp = deviceProxy
       thread = threading.Thread(target=self.run, args=())
       thread.daemon = True
       thread.start()

    def run(self):
       while True:
           hb = self.dp.HeartBeat
           diff = (datetime.utcnow() - 
                datetime.strptime(hb, '%Y-%m-%d %H:%M:%S.%f'))
           seconds = int(diff.total_seconds())
           if seconds > 60:
               print(("WARNING No heartbeat since {} - {} seconds ago -" +
                     " has watchdog died?").format(hb,seconds))

           time.sleep(30)

class CallBack(object):

    def __init__(self, devProxy):
         self.firstCall = True
         period = devProxy.get_attribute_poll_period('targetState')
         if period == 0:
              print('Setting polling on attribute "targetState" to 3s')
              devProxy.poll_attribute('targetState', 3000)

    def push_event(self, evt):
         print("In push_event()")
         #pdb.set_trace() 
         if self.firstCall:
               self.firstCall = False
               print('First callback ... not a real change')
               return
         if not evt.err and evt.event == 'change':
             age = int(time.time()) - evt.attr_value.time.tv_sec
             print(evt.attr_value.value,age)
             
        
# Connect to the Server

os.environ['TANGO_HOST'] = 'localhost:20000'

dev = DeviceProxy('sdp/elt/master')

hb = HeartBeat(dev)
cb = CallBack(dev)
dev.subscribe_event('targetState',tango.EventType.CHANGE_EVENT, cb, [])
#while True:
#    time.sleep(10)
#    print("Still waiting.....")
state = input('Master Controller state {} Enter target state....'
        .format(dev.status()))
print(state)

