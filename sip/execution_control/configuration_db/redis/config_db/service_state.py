# -*- coding: utf-8 -*-
"""High-level service state API."""
import logging

from .state_object import StateObject

LOG = logging.getLogger('SIP.EC.CDB')


class ServiceState(StateObject):
    """SDP state data object."""

    def __init__(self, subsystem: str, name: str, version: str):
        """Initialise SDP state data object."""
        StateObject.__init__(self, self.get_service_state_object_id(
            subsystem, name, version))

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
