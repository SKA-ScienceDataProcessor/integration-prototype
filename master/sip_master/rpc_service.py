import rpyc
from sip_common import logger
from sip_master import config

""" Master controller rpyc server

This is a rpyc service where the commands starting with 'exposed_'
are available to the client - less the 'exposed_' text

    Example client code:
       conn=rpyc.connect('localhost',port=12345)
       result = conn.root.offline()

A (tpd) command returning a value with client arguments
       retval=conn.root.tpd_command(arg1,arg2,arg3)
"""
__author__ = 'Brian McIlwrath'


class RpcService(rpyc.Service):
    def on_connect(self):
        logger.info(" master controller client controller connected")

    def on_disconnect(self):
        logger.info("master controller client controller disconnected")

    def exposed_online(self,callback=None):
        return config.state_machine.post_event(['online'])

    def exposed_capability(self, name, type, callback=None):
        return config.state_machine.post_event(['cap', name, type])

    def exposed_offline(self,callback=None):
        return config.state_machine.post_event(['offline'])

    def exposed_shutdown(self,callback=None):
        return config.state_machine.post_event(['shutdown'])

    def exposed_get_current_state(self):
        return config.state_machine.current_state()

