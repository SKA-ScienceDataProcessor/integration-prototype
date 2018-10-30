# -*- coding: utf-8 -*-
"""High Level Master Controller Client API.

FIXME(BM): should have the following public methods
    * set_target_state
    * get_target_state
    * get_current_state
"""
import logging

from datetime import datetime

from .config_db_redis import ConfigDb
from . import events

LOG = logging.getLogger('SIP.EC.CDB')
MC_AGGREGATE_TYPE = 'execution_control'
SDP_AGGREGATE_TYPE = 'sdp_components'
MC_KEY = 'master_controller'


class SDPStates:
    """Master Controller Client Interface."""

    def __init__(self):
        """Initialise the client."""
        self._db = ConfigDb()
        self._events = events

    ###########################################################################
    # PubSub functions
    ###########################################################################

    def subscribe(self, subscriber: str) -> events.EventQueue:
        """Subscribe to Master Controller events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return self._events.subscribe(MC_AGGREGATE_TYPE, subscriber)

    def get_subscribers(self):
        """Get the list of subscribers to Master Controller events.

        Returns:
            List[str], list of subscriber names.

        """
        return self._events.get_subscribers(MC_AGGREGATE_TYPE)

    def publish(self, key: str, event_type: str,
                event_data: dict = None):
        """Publish a Master Controller event.

        Args:
            key (str): Master controller or sdp components.
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        self._events.publish(MC_AGGREGATE_TYPE, key, event_type,
                             event_data)

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_value(self, key: str, field: str):
        """Get value associated to the field in string.

        Args:
              key (str) : Master controller or sdp components.
              field (str): Field
        Returns:
            str, value of a specified key and field

        """
        aggregate_type = self._get_aggregate_type(key)
        value = self._db.get_hash_value(self._get_key(key, aggregate_type),
                                        field)
        if value:
            return value
        return None

    def get_active(self):
        """Get the list of active master controller from the database.

        Returns:
            list, list of active master controller

        """
        return self._db.get_list('{}:active'.format(MC_AGGREGATE_TYPE))

    def get_completed(self):
        """Get the list of completed master controller from the database.

        Returns:
            list, list of completed master controller

        """
        return self._db.get_list('{}:completed'.format(MC_AGGREGATE_TYPE))

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_target_state(self, state_field, value):
        """Update the target state.

        Args:
            state_field (str): state_field that will be updated
            value (str): New value for target state

        """
        aggregate_type = self._get_aggregate_type(MC_KEY)
        mc_key = self._get_key(MC_KEY, aggregate_type)

        # Setting UTC time
        current_time = datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S.%f')
        self._db.set_hash_value(mc_key, state_field, value, pipeline=True)
        self._db.set_hash_value(mc_key, "Target_timestamp", current_time,
                                pipeline=True)
        self._db.execute()
        target_list_key = '{}:active'.format(aggregate_type)
        self._db.append_to_list(target_list_key, MC_KEY)

        # Publish an event to notify subscribers of the change in target state
        self.publish(MC_KEY, 'updated')

    def update_sdp_state(self, state_field, value):
        """Update the SDP state.

        Args:
            state_field (str): State field that will be updated
            value (str): New value for sdp state

        """
        # TODO(NJT) move this hardcoded key and field to a function?
        aggregate_type = self._get_aggregate_type(MC_KEY)
        mc_key = self._get_key(MC_KEY, aggregate_type)
        LOG.debug('State Update is Completed %s', mc_key)

        # Check that the key exists!
        if not self._db.get_keys(mc_key):
            raise KeyError('Master Controller key is not found: {}'
                           .format(mc_key))

        current_time = datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S.%f')
        self.publish(MC_KEY, 'completed')
        self._db.set_hash_value(mc_key, state_field, value, pipeline=True)
        self._db.set_hash_value(mc_key, "State_timestamp", current_time,
                                pipeline=True)
        self._db.remove_element('{}:active'.format(aggregate_type), 0,
                                MC_KEY, pipeline=True)
        self._db.append_to_list('{}:completed'.format(aggregate_type),
                                MC_KEY, pipeline=True)
        self._db.execute()

    def update_component_state(self, key, field, value):
        """Update the state of the given key and field.

        Args:
            key (str): Master controller or sdp components
            field (str): Field of the value that will be updated
            value (str): New value for the given state

        """
        aggregate_type = self._get_aggregate_type(key)
        component_key = self._get_key(key, aggregate_type)
        self._db.set_hash_value(component_key, field, value)

    ###########################################################################
    # Private functions
    ###########################################################################

    @staticmethod
    def _get_key(key_type: str, aggregate_type: str) -> str:
        """Return a master controller db key.

        Args:
            key_type (str): Master controller or sdp components
            aggregate_type (str): Aggregate type

        Returns:
            str, db key for the specified type.

        """
        return '{}:{}'.format(aggregate_type, key_type)

    @staticmethod
    def _get_aggregate_type(key: str) -> str:
        """Get the correct aggregate type.

        Args:
            key (str): Master controller or sdp components

        Returns:
            str, aggregate type for the specified key

        """
        if key == 'master_controller':
            aggregate_type = MC_AGGREGATE_TYPE
        else:
            aggregate_type = SDP_AGGREGATE_TYPE
        return aggregate_type

    # #########################################################################
    # Utility functions
    # #########################################################################

    def clear(self):
        """Clear / drop the entire database.

        Note:
            Use with care!
        """
        self._db.flush_db()
