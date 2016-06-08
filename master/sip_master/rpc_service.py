""" Master controller rpyc server
"""
__author__ = 'Brian McIlwrath'

import rpyc
from sip_common import logger
from sip_master import config

""" This is a rpyc service where the commands starting with 'exposed_'
    are available to the client - less the 'exposed_' text
    Example client code:
       conn=rpyc.connect('localhost',port=12345)
  :    conn.root.command('offline')

A (tpd) command returning a value with client arguments
       retval=conn.root.tpd_command(arg1,arg2,arg3)
"""

class RpcService(rpyc.Service):
   def on_connect(self):
      logger.info(" master controller client controller connected")
   def on_disconnect(self):
      logger.info("master controller client controller disconnected")
   def exposed_command(self, state_command,callback=None):
      config.state_machine.post_event([state_command])
      if(callback != None):
         callback(state_command)
   def exposed_get_current_state(self):
      return config.state_machine.current_state()

