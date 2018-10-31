# -*- coding: utf-8 -*-
"""Base class for State objects."""
import logging

from datetime import datetime

from .config_db_redis import ConfigDb
from . import events

LOG = logging.getLogger('SIP.EC.CDB')
AGGREGATE_TYPE = 'states'


class StateObject:
    """Base class for state objects (service state & sdp state)."""

    def __init__(self, aggregate_id: str):
        """Initialise the client."""
        self._db = ConfigDb()
        self._events = events
        self._aggregate_id = aggregate_id
        self._key = '{}:{}'.format(AGGREGATE_TYPE, self._aggregate_id)

        if not self._db.key_exists(self._key):
            self._db.set_hash_values(self._key, self._initial_state_config())

        # # FIXME(BM) this should not be hardcoded and perhaps moved to the \
        # # service_state class?
        # service_list = [
        #     'ExecutionControl:MasterController:test',
        #     'ExecutionControl:ProcessingController:test',
        #     'ExecutionControl:Alerts:test',
        #     'TangoControl:SDPMaster:test',
        #     'TangoControl:ProcessingInterface:test',
        #     'TangoControl:Logger:test',
        #     'TangoControl:Alarms:test',
        #     'Platform:DockerSwarm:test',
        #     'Platform:Logger:test',
        #     'Platform:Metrics:test'
        # ]
        # for service in service_list:
        #     _key = 'states:service_state:{}'.format(service)
        #     if not self._db.key_exists(_key):
        #         self._db.set_hash_values(_key, self._initial_state_config())

    ###########################################################################
    # Pub/Sub functions
    ###########################################################################

    def subscribe(self, subscriber: str) -> events.EventQueue:
        """Subscribe to state events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return self._events.subscribe(AGGREGATE_TYPE, subscriber)

    def get_subscribers(self):
        """Get the list of subscribers to state events.

        Returns:
            List[str], list of subscriber names.

        """
        return self._events.get_subscribers(AGGREGATE_TYPE)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish an state event.

        Args:
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        self._events.publish(AGGREGATE_TYPE, self._aggregate_id,
                             event_type, event_data)

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_current_state(self) -> str:
        """Get the current state."""
        state = self._db.get_hash_value(self._key, 'current_state')
        return state

    def get_target_state(self) -> str:
        """Get the target state."""
        state = self._db.get_hash_value(self._key, 'target_state')
        return state

    def get_current_state_timestamp(self) -> datetime:
        """Get the current state timestamp."""
        timestamp = self._db.get_hash_value(self._key, 'current_timestamp')
        # return datetime.fromisoformat(timestamp)
        return self._datetime_from_isoformat(timestamp)

    def get_target_state_timestamp(self) -> datetime:
        """Get the target state timestamp."""
        timestamp = self._db.get_hash_value(self._key, 'target_timestamp')
        # return datetime.fromisoformat(timestamp)
        return self._datetime_from_isoformat(timestamp)

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_target_state(self, value: str) -> datetime:
        """Set the target state.

        TODO(BM) check value is an allowed state.

        Args:
            value (str): New value for target state

        Returns:
            datetime, update timestamp

        """
        timestamp = datetime.utcnow()
        self._db.set_hash_value(self._key, 'target_state', value,
                                pipeline=True)
        self._db.set_hash_value(self._key, 'target_timestamp',
                                timestamp.isoformat(), pipeline=True)
        self._db.execute()

        # Publish an event to notify subscribers of the change in state
        self.publish('target_state_updated')

        return timestamp

    def update_current_state(self, value: str) -> datetime:
        """Update the current state.

        TODO(BM) check value is an allowed state.

        Args:
            value (str): New value for sdp state

        Returns:
            datetime, update timestamp

        """
        timestamp = datetime.utcnow()
        self._db.set_hash_value(self._key, 'current_state', value,
                                pipeline=True)
        self._db.set_hash_value(self._key, 'current_timestamp',
                                timestamp.isoformat(), pipeline=True)
        self._db.execute()

        # Publish an event to notify subscribers of the change in state
        self.publish('current_state_updated')

        return timestamp

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
            current_state='UNKNOWN',
            target_state='UNKNOWN',
            current_timestamp=datetime.utcnow().isoformat(),
            target_timestamp=datetime.utcnow().isoformat())
        return _initial_state

    @staticmethod
    def _datetime_from_isoformat(value: str):
        """Return a datetime object from an isoformat string."""
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')

    # #########################################################################
    # Utility functions
    # #########################################################################

    def clear(self):
        """Clear / drop the entire database.

        Note:
            Use with care!

        FIXME(BM) this should only clear the SDP state keys
        """
        self._db.flush_db()
