# -*- coding: utf-8 -*-
"""High-level service state API."""
import logging

from .state_object import StateObject

LOG = logging.getLogger('SIP.EC.CDB')


class ServiceState(StateObject):
    """SDP state data object."""

    # Allowed service states
    _allowed_states = ['init', 'on', 'off', 'alarm', 'fault']

    # Allowed transitions when setting the current state.
    # key == current state, value == allowed transitions
    _allowed_transitions = dict(
        init=['on', 'alarm', 'fault'],
        on=['off', 'alarm', 'fault'],
        alarm=['off', 'on', 'fault', 'init'],
        fault=['off'],
        off=[]
    )

    # Allowed transitions when setting the target state.
    # key == current state, value == allowed target states
    _allowed_target_states = dict(
        init=[],
        on=['off'],
        alarm=['reset', 'off'],
        fault=['off'],
        off=[]
    )

    def __init__(self, subsystem: str, name: str, version: str):
        """Initialise SDP state data object."""
        _id = self.get_service_state_object_id(subsystem, name, version)
        StateObject.__init__(self, _id,
                             self._allowed_states,
                             self._allowed_transitions,
                             self._allowed_target_states)

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
