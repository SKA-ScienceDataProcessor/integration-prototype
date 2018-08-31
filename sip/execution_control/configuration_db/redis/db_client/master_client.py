# -*- coding: utf-8 -*-
"""High Level Master Controller Client API."""
import ast
import logging
import time

from .config_db_redis import ConfigDb
from . import events
from .event_keys import aggregate_events_data, aggregate_events_list

LOG = logging.getLogger('SIP.EC.CDB')
MC_AGGREGATE_TYPE = 'execution_control'
SDP_AGGREGATE_TYPE = 'sdp_components'


class MasterDbClient:
    """Master Controller Client Interface."""

    def __init__(self):
        """Initialise the client."""
        self._db = ConfigDb()
        self._events = events

    ###########################################################################
    # PubSub functions
    ###########################################################################

    def subscribe(self, subscriber: str, ) -> events.EventQueue:
        """Subscribe to Scheduling Block Instance (SBI) events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return self._events.subscribe(MC_AGGREGATE_TYPE, subscriber)

    def get_subscribers(self):
        """Get the list of subscribers to Scheduling Block Instance (SBI) events.

        Returns:
            List[str], list of subscriber names.

        """
        return self._events.get_subscribers(MC_AGGREGATE_TYPE)

    def publish(self, block_id: str, event_type: str, event_data: dict = None):
        """Publish a SBI event.

        Args:
            block_id (str):
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        self._events.publish(MC_AGGREGATE_TYPE, block_id, event_type, event_data)

    ###########################################################################
    # Get functions
    ###########################################################################

    def get_value(self, key, field):
        """Get value associated to the field in string.

        Args:
              key (str)
              field (str)
        """

        aggregate_type = self._get_aggregate_type(key)

        value = self._db.get_hash_value(self._get_key(key, aggregate_type),
                                        field)
        if value:
            return value
        return None

    # def get_value_bool(self, key, field):
    #     """Get the value associated to the field in boolean."""
    #     value = self.get_value(key, field)
    #     return bool(value)

    def get_all_value(self, key):
        """Get all the value associated to the name, returned in dict."""
        value = self._db.get_hash_dict(key)
        if value:
            return value
        return None

    def get_service_list(self, key):
        """Get the service list from the database."""
        # Initialise empty list
        list_eval = []

        services = self._db.get_list(key)
        if services:
            for service_list in services:
                list_eval.append(ast.literal_eval(service_list))

        # TODO: (NJT) Need to test this function to check if it returns list
        return list_eval

    def get_service_from_list(self, key, index):
        """Get the n'th element of the service list.

        If the does not point to an element 0 is returned.
        """
        element = self._db.get_list_value(key, index)
        if element:
            element_eval = ast.literal_eval(element)
            return element_eval
        return 0

    # def get_service_from_list_bool(self, key, index):
    #     """Get the n'th element of the service list in boolean.
    #
    #     If the does not point to an element 0 is returned.
    #     """
    #     service = self.get_service_from_list(key, index)
    #     for entry in service:
    #         if service[entry] == 'true' or 'false' or 'True' or 'False':
    #             bool(service[entry])
    #         return service

    def get_service_list_length(self, key):
        """Get the length of the service list.

        If the does not point to a list 0 is returned.
        """
        list_length = self._db.get_list_length(key)
        if list_length:
            return list_length
        return 0

    def get_active(self):
        """Get the list of active scheduling block instance or processing
        block from the database.

        Returns:
            list, Scheduling block instance or processing block ids

        """
        return self._db.get_list('{}:active'.format(MC_AGGREGATE_TYPE))

    def get_completed(self):
        """Get the list of completed scheduling block instance or processing
         block from the database.

        Returns:
            list, Scheduling block instance or processing block ids

        """
        return self._db.get_list('{}:completed'.format(MC_AGGREGATE_TYPE))

    ###########################################################################
    # Add functions
    ###########################################################################

    def add_service_to_list(self, key, element):
        """Add a new service to the end of the list."""
        self._db.prepend_to_list(key, element)

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_target_state(self, key, field, value):
        """Update the target state.

        Args:
              key (str):
              field (str):
              value (str):

        """
        mc_key = self._get_key(key, MC_AGGREGATE_TYPE)
        current_time = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())
        self._db.set_hash_value(mc_key, field, value, pipeline=True)
        self._db.set_hash_value(mc_key, "Target_timestamp", current_time,
                                pipeline=True)
        self._db.execute()
        target_list_key = '{}:active'.format(MC_AGGREGATE_TYPE)
        print(target_list_key)
        self._db.append_to_list(target_list_key, key)

        # Publish an event to notify subscribers of the change in target state
        self.publish(key, 'updated')

    def update_sdp_state(self, key, field, value):
        """Update the target state.

        Args:
              key (str):
              field (str):
              value (str):
        """

        # TODO (NJT) Currently there is no way to differentiate between the key
        # TODO       Therefore, need to find a to do that. It works fine for now.
        mc_key = self._get_key(key, MC_AGGREGATE_TYPE)
        LOG.debug('State Updated is Completed %s', mc_key)

        # Check that the key exists!
        if not self._db.get_keys(mc_key):
            raise KeyError('Master Controller key is not found: {}'
                           .format(mc_key))

        current_time = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())
        self.publish(key, 'completed')
        self._db.set_hash_value(mc_key, field, value, pipeline=True)
        self._db.set_hash_value(mc_key, "State_timestamp", current_time,
                                pipeline=True)
        self._db.remove_element('{}:active'.format(MC_AGGREGATE_TYPE), 0,
                                key, pipeline=True)
        self._db.append_to_list('{}:completed'.format(MC_AGGREGATE_TYPE),
                                key, pipeline=True)
        self._db.execute()

    def update_component_state(self, key, field, value):
        """Update the state of the given key and field.

        Args:
              key (str):
              field (str):
              value (str):
        """
        component_key = self._get_key(key, SDP_AGGREGATE_TYPE)
        self._db.set_hash_value(component_key, field, value)

    ###########################################################################
    # Private functions
    ###########################################################################

    @staticmethod
    def _get_key(key: str, aggregate_type: str) -> str:
        """Return a master controller db key.

        Args:
            key (str):
            aggregate_type (str): Aggregate type

        Returns:
            str, db key for the specified SBI

        """
        return '{}:{}'.format(aggregate_type, key)

    @staticmethod
    def _get_aggregate_type(key: str) -> str:
        """Get the correct aggregate type

        Args:
              key (str):

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
