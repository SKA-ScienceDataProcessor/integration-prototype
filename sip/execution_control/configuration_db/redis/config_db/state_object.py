# -*- coding: utf-8 -*-
"""Base class for State objects."""
import logging
from typing import List

from datetime import datetime

from .config_db_redis import ConfigDb
from . import events

LOG = logging.getLogger('SIP.EC.CDB')
AGGREGATE_TYPE = 'states'
DB = ConfigDb()


class StateObject:
    """Base class for state objects (service state & sdp state)."""

    def __init__(self, aggregate_id: str, states: List[str],
                 allowed_transitions: dict, allowed_commands: dict):
        """Initialise the client."""
        self._id = aggregate_id
        self._key = '{}:{}'.format(AGGREGATE_TYPE, self._id)
        self._states = states
        self._allowed_transitions = allowed_transitions
        self._allowed_commands = allowed_commands
        if not DB.key_exists(self._key):
            DB.set_hash_values(self._key, self._initial_state_config())

    @property
    def current_state(self) -> str:
        """Get the current state."""
        return DB.get_hash_value(self._key, 'current_state')

    @property
    def target_state(self) -> str:
        """Get the target state."""
        return DB.get_hash_value(self._key, 'target_state')

    @property
    def current_timestamp(self) -> datetime:
        """Get the current state timestamp."""
        timestamp = DB.get_hash_value(self._key, 'current_timestamp')
        return self._datetime_from_isoformat(timestamp)

    @property
    def target_timestamp(self) -> datetime:
        """Get the target state timestamp."""
        timestamp = DB.get_hash_value(self._key, 'target_timestamp')
        return self._datetime_from_isoformat(timestamp)

    @target_state.setter
    def target_state(self, value: str):
        """Set the target state."""
        self.update_current_state(value)

    def update_target_state(self, value: str) -> datetime:
        """Set the target state.

        TODO(BM) check value is an allowed state... this will need to know
                 the allowed state transitions from the child class.

        Args:
            value (str): New value for target state

        Returns:
            datetime, update timestamp

        """
        return self._update_state('target', value)

    def update_current_state(self, value: str) -> datetime:
        """Update the current state.

        TODO(BM) check value is an allowed state.

        Args:
            value (str): New value for sdp state

        Returns:
            datetime, update timestamp

        """
        return self._update_state('current', value)

    ###########################################################################
    # Pub/Sub functions
    ###########################################################################

    @staticmethod
    def subscribe(subscriber: str) -> events.EventQueue:
        """Subscribe to state events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying events.

        """
        return events.subscribe(AGGREGATE_TYPE, subscriber)

    @staticmethod
    def get_subscribers():
        """Get the list of subscribers to state events.

        Returns:
            List[str], list of subscriber names.

        """
        return events.get_subscribers(AGGREGATE_TYPE)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish an state event.

        Args:
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        events.publish(AGGREGATE_TYPE, self._id, event_type,
                       event_data)

    ###########################################################################
    # Private functions
    ###########################################################################

    @staticmethod
    def _initial_state_config() -> dict:
        """Return a dictionary used to initialise a state object.

        This method is used to obtain a dictionary/hash describing the initial
        state of SDP or a service in SDP.

        Returns:
            dict, Initial state configuration

        """
        _initial_state = dict(
            current_state='unknown',
            target_state='unknown',
            current_timestamp=datetime.utcnow().isoformat(),
            target_timestamp=datetime.utcnow().isoformat())
        return _initial_state

    @staticmethod
    def _datetime_from_isoformat(value: str):
        """Return a datetime object from an isoformat string."""
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')

    def _update_state(self, state_type: str, value: str):
        """Update the state of type specified (current or target).

        Args:
            state_type(str): Type of state to update, current or target.
            value (str): New state value.

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
                     event_data=dict(old_state=old_state, new_state=value))

        return timestamp
