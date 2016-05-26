""" Master controller rpyc server
"""
__author__ = 'Brian McIlwrath'

import rpyc
from ._states import mc

class MasterControllerService(rpyc.Service):
   def on_connect(self):
      print (" master controller connected")
   def on_disconnect(self):
      print ("master controller disconnected")
   def exposed_command(self, state_command):
      mc.post_event([state_command])
   def exposed_command_and_cb(self, state_command,callback):
      mc.post_event([state_command])
      callback(state_command)
   def exposed_callback(self,func,text):
      func(text)
