# -*- coding: utf-8 -*-
"""High-level SDP state API."""
import logging

from .state_object import StateObject

LOG = logging.getLogger('SIP.EC.CDB')


class SDPState(StateObject):
    """SDP state data object."""

    def __init__(self):
        """Initialise SDP state data object."""
        StateObject.__init__(self, 'sdp_state')
