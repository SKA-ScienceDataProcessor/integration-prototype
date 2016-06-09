""" Prototype Slave rpyc server
"""
__author__ = 'Brian McIlwrath'

import rpyc
from sip_common import logger

class SlaveService(rpyc.Service):
   def on_connect(self):
      logger.info("slave service connected")
   def on_disconnect(self):
      logger.info("slave service disconnected")
   def exposed_get_current_state(self):
      return 'SIP Slave test reply - OK!'
