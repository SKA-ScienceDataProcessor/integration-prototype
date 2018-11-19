# -*- coding: utf-8 -*-
"""Base class for State objects."""
import inspect
import os
from datetime import datetime
from typing import List

from .. import DB, _events, LOG
from ..utils.datetime_utils import datetime_from_isoformat
from ._keys import STATES_KEY


class StateObject:
    """Base class for state objects (service state & sdp state)."""

    def __init__(self, object_id: str, allowed_states: List[str],
                 allowed_transitions: dict, allowed_target_states: dict):
        """Initialise a state object.

        Args:
            allowed_states (List[str]): List of allowed states.
            allowed_transitions (dict): Dict of allowed state transitions
            allowed_target_states (dict): Dict of allowed target states

        """
        self._id = object_id
        self._type = STATES_KEY  # object type
        self._key = '{}:{}'.format(STATES_KEY, self._id)
        self._allowed_states = [state.lower() for state in allowed_states]
        self._allowed_transitions = self._dict_lower(allowed_transitions)
        self._allowed_target_states = self._dict_lower(allowed_target_states)
        if not DB.key_exists(self._key):
            DB.set_hash_values(self._key, self._initialise())

    @property
    def id(self) -> str:
        """Return the object id."""
        return self._id

    @property
    def allowed_states(self) -> List[str]:
        """Get list of allowed object states."""
        return self._allowed_states

    @property
    def allowed_state_transitions(self) -> dict:
        """Get dictionary of allowed state transitions."""
        return self._allowed_transitions

    @property
    def allowed_target_states(self) -> dict:
        """Get dictionary of allowed target states / commands."""
        return self._allowed_target_states

    @property
    def current_state(self) -> str:
        """Get the current state."""
        return DB.get_hash_value(self._key, 'current_state')

    @current_state.setter
    def current_state(self, value):
        """Set the current state."""
        self.update_current_state(value)

    @property
    def target_state(self) -> str:
        """Get the target state."""
        return DB.get_hash_value(self._key, 'target_state')

    @target_state.setter
    def target_state(self, value):
        """Set the target state."""
        self.update_target_state(value)

    @property
    def current_timestamp(self) -> datetime:
        """Get the current state timestamp."""
        timestamp = DB.get_hash_value(self._key, 'current_timestamp')
        return datetime_from_isoformat(timestamp)

    @property
    def target_timestamp(self) -> datetime:
        """Get the target state timestamp."""
        timestamp = DB.get_hash_value(self._key, 'target_timestamp')
        return datetime_from_isoformat(timestamp)

    def update_target_state(self, value: str) -> datetime:
        """Set the target state.

        Args:
            value (str): New value for target state

        Returns:
            datetime, update timestamp

        Raises:
            RuntimeError, if it is not possible to currently set the target
            state.
            ValueError, if the specified target stat is not allowed.

        """
        value = value.lower()
        current_state = self.current_state
        if current_state == 'unknown':
            raise RuntimeError("Unable to set target state when current state "
                               "is 'unknown'")

        allowed_target_states = self._allowed_transitions[current_state]

        LOG.debug('Updating target state of %s to %s', self._id, value)

        if value not in allowed_target_states:
            raise ValueError("Invalid target state: '{}'. {} can be "
                             "commanded to states: {}".
                             format(value, current_state,
                                    allowed_target_states))

        return self._update_state('target', value)

    def update_current_state(self, value: str) -> datetime:
        """Update the current state.

        Args:
            value (str): New value for sdp state

        Returns:
            datetime, update timestamp

        Raises:
            ValueError: If the specified current state is not allowed.

        """
        value = value.lower()
        current_state = self.current_state
        # IF the current state is unknown, it can be set to any of the allowed
        # states, otherwise only allow certain transitions.
        if current_state == 'unknown':
            allowed_transitions = self._allowed_states
        else:
            allowed_transitions = self._allowed_transitions[current_state]
            allowed_transitions.append(current_state)

        LOG.debug('Updating current state of %s to %s', self._id, value)

        if value not in allowed_transitions:
            raise ValueError("Invalid current state update: '{}'. '{}' can be "
                             "transitioned to states: {}"
                             .format(value, current_state,
                                     allowed_transitions))

        return self._update_state('current', value)

    ###########################################################################
    # Pub/Sub functions
    ###########################################################################

    @staticmethod
    def subscribe(subscriber: str) -> _events.EventQueue:
        """Subscribe to state events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying events.

        """
        return _events.subscribe(STATES_KEY, subscriber)

    @staticmethod
    def get_subscribers() -> List[str]:
        """Get the list of subscribers to state events.

        Returns:
            List[str], list of subscriber names.

        """
        return _events.get_subscribers(STATES_KEY)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish an state event.

        Args:
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        _stack = inspect.stack()
        _origin = (os.path.basename(_stack[3][1]) + '::' +
                   _stack[3][3]+'::L{}'.format(_stack[3][2]))
        _events.publish(event_type=event_type,
                        event_data=event_data,
                        object_type=self._type,
                        object_id=self._id,
                        object_key=self._key,
                        origin=_origin)

    ###########################################################################
    # Private functions
    ###########################################################################

    def _initialise(self, initial_state: str = 'unknown') -> dict:
        """Return a dictionary used to initialise a state object.

        This method is used to obtain a dictionary/hash describing the initial
        state of SDP or a service in SDP.

        Args:
            initial_state (str): Initial state.

        Returns:
            dict, Initial state configuration

        """
        initial_state = initial_state.lower()
        if initial_state != 'unknown' and \
                initial_state not in self._allowed_states:
            raise ValueError('Invalid initial state: {}'.format(initial_state))
        _initial_state = dict(
            current_state=initial_state,
            target_state=initial_state,
            current_timestamp=datetime.utcnow().isoformat(),
            target_timestamp=datetime.utcnow().isoformat())
        return _initial_state

    def _update_state(self, state_type: str, value: str) -> datetime:
        """Update the state of type specified (current or target).

        Args:
            state_type(str): Type of state to update, current or target.
            value (str): New state value.

        Returns:
            timestamp, current time

        """
        timestamp = datetime.utcnow()
        field = '{}_state'.format(state_type)
        old_state = DB.get_hash_value(self._key, field)
        DB.set_hash_value(self._key, field, value, pipeline=True)
        DB.set_hash_value(self._key, '{}_timestamp'.format(state_type),
                          timestamp.isoformat(), pipeline=True)
        DB.execute()

        # Publish an event to notify subscribers of the change in state
        self.publish('{}_state_updated'.format(state_type),
                     event_data=dict(state=value, old_state=old_state))

        return timestamp

    @staticmethod
    def _dict_lower(dictionary: dict):
        """Convert allowed state transitions / target states to lowercase."""
        return {key.lower(): [value.lower() for value in value]
                for key, value in dictionary.items()}

    def __repr__(self):
        """Get a string representation of a State object."""
        return self._id
