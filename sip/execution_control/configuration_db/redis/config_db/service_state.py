# -*- coding: utf-8 -*-
"""High-level service state API."""
import logging

from .state_object import StateObject

LOG = logging.getLogger('SIP.EC.CDB')


class ServiceState(StateObject):
    """SDP state data object."""

    _states = ['init', 'on', 'off', 'alarm', 'fault']
    _transitions = dict(
        init=['on', 'alarm', 'fault'],
        on=['off', 'alarm', 'fault'],
        off=['alarm', 'fault'],
        alarm=['on', 'fault', 'init'],
        fault=[]
    )
    _commands = dict(
        init=[],
        on=['off'],
        off=[],
        alarm=['reset'],
        fault=[]
    )

    def __init__(self, subsystem: str, name: str, version: str):
        """Initialise SDP state data object."""
        _id = self.get_service_state_object_id(subsystem, name, version)
        StateObject.__init__(self, _id, self._states, self._transitions,
                             self._commands)

    @staticmethod
    def get_service_state_object_id(subsystem: str, name: str,
                                    version: str) -> str:
        """Return service state data object key.

        Args:
            subsystem (str): Subsystem the service belongs to
            name (str): Name of the Service
            version (str): Version of the Service

        Returns:
            str, Key used to store the service state data object

        """
        return '{}.{}.{}'.format(subsystem, name, version)
