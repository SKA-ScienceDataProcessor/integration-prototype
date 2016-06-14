""" rpyc server interface for a slave controller
"""
__author__ = 'Brian McIlwrath'

import os
import rpyc
import threading
import time

from sip_common import logger
from sip_slave.load import load
from sip_slave.unload import unload
from sip_slave import config

class _Shutdown(threading.Thread):
    """ Shutdown the slave

    This is run in a separate thread so the that the rpc shutdown function
    can return to its caller. If we don't do this, the master controller
    hangs.
    """
    def __init__(self):
        super(_Shutdown, self).__init__()
    def run(self):
        logger.info('slave exiting')

        # Give time for the rpc to return
        time.sleep(1)

        # Exit the application
        os._exit(0)

class SlaveService(rpyc.Service):
   #def on_connect(self):
   #    logger.info("slave service connected")
   #def on_disconnect(self):
   #    logger.info("slave service disconnected")
   def exposed_get_state(self):
       return config.state
   def exposed_load(self):
       load()
   def exposed_unload(self):
       unload()
   def exposed_shutdown(self):
       _Shutdown().start()
