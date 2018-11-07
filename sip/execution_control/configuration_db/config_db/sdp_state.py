# -*- coding: utf-8 -*-
"""High-level SDP state API."""
import logging

from .state_object import StateObject

LOG = logging.getLogger('SIP.EC.CDB')


class SDPState(StateObject):
    """SDP state data object."""

    # Allowed service states
    _allowed_states = ['init', 'standby', 'on', 'off', 'disable',
                       'alarm', 'fault']

    # Allowed transitions when setting the current state.
    # key == current state, value == allowed transitions
    _allowed_transitions = dict(
        init=['standby', 'alarm', 'fault'],
        standby=['off', 'on', 'alarm', 'fault'],
        on=['off', 'standby', 'disable', 'alarm', 'fault'],
        off=['alarm', 'fault'],
        disable=['on', 'off', 'standby'],
        alarm=['fault', 'init', 'standby', 'on', 'off', 'disable'],
        fault=[]
    )

    # Allowed transitions when setting the target state.
    # key == current state, value == allowed target states
    _allowed_target_states = dict(
        init=[],
        standby=['off', 'on'],
        on=['off', 'standby', 'disable'],
        off=[],
        disable=['off', 'on', 'standby'],
        alarm=['reset'],
        fault=[]
    )

    def __init__(self):
        """Initialise SDP state data object."""
        StateObject.__init__(self, 'sdp_state',
                             self._allowed_states,
                             self._allowed_transitions,
                             self._allowed_target_states)
