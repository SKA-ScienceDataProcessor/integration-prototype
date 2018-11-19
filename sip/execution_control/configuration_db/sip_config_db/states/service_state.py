# -*- coding: utf-8 -*-
"""High-level service state API."""
import re

from ._state_object import StateObject


class ServiceState(StateObject):
    """SDP state data object."""

    _allowed_subsystems = [
        'TangoControl',
        'ExecutionControl',
        'ExecutionEngine',
        'SDPServices',
        'Platform'
    ]

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
        if not re.match(r'^\d+.\d+.\d+|test$', version):
            raise ValueError('Invalid version {}'.format(version))
        if subsystem not in self._allowed_subsystems:
            raise ValueError('Invalid subsystem {} (allowed: {})'
                             .format(subsystem, self._allowed_subsystems))
        _id = self.get_service_state_object_id(subsystem, name, version)
        self._subsystem = subsystem
        self._name = name
        self._version = version
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
        return '{}:{}:{}'.format(subsystem, name, version)

    @property
    def subsystem(self):
        """Get the subsystem the service belongs to."""
        return self._subsystem

    @property
    def name(self):
        """Get the name of the service."""
        return self._name

    @property
    def version(self):
        """Get the version of the service."""
        return self._version
