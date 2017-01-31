# -*- coding: utf-8 -*-
"""Master controller rpyc server."""
__author__ = 'Brian McIlwrath'

import rpyc
from sip_common.logging_api import log
from sip_master import config


class RpcService(rpyc.Service):
    """Master Controller RPC control interface.

    This is an rpyc service where the commands starting with ``exposed_``
    are available to the client - less the ``exposed_`` text

    **Example client code**::

        import rpyc
        conn = rpyc.connect(host='localhost', port=12345)
        result = conn.root.offline()
    """
    def on_connect(self):
        """Called when connecting to the RPC service."""
        log.info("master controller client controller connected")

    def on_disconnect(self):
        """Called when disconnecting from the RPC service."""
        log.info("master controller client controller disconnected")

    def exposed_online(self, callback=None):
        """Exposed online method.
        Sends the :code:`online` command to the Master Controller state machine."""
        return config.state_machine.post_event(['online'])

    def exposed_capability(self, name, type, callback=None):
        """Exposed capability method.
        Sends the :code:`cap` command to the Master Controller state machine.

        Args:
            name (str): The name of the capability.
            type (str): The type of the capability.
        """
        return config.state_machine.post_event(['cap', name, type])

    def exposed_offline(self,callback=None):
        """Exposed capability method.
        Sends the :code:`cap` command to the Master Controller state machine."""
        return config.state_machine.post_event(['offline'])

    def exposed_shutdown(self,callback=None):
        """Exposed shutdown method.
        Sends the :code:`shutdown` command to the Master Controller state
        machine."""
        return config.state_machine.post_event(['shutdown'])

    def exposed_get_current_state(self):
        """Exposed get_current_state method.
        Returns the current state of Master Controller state machine.

        Returns:
            str: Master Controller state
        """
        return config.state_machine.current_state()

