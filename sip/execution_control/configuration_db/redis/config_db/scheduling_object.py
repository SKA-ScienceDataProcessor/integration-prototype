# -*- coding: utf-8 -*-
"""Base class for scheduling or processing block data objects."""
import ast
import logging
from typing import List

from . import event_keys, events
from .config_db_redis import ConfigDb

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()

PB_TYPE_PREFIX = 'pb'
SBI_TYPE_PREFIX = 'sbi'


class SchedulingObject:
    """Base class for SBI and PB data objects API."""

    def __init__(self, aggregate_type: str, aggregate_id: str = None):
        """Initialise variables.

        Args:
            aggregate_type (str): Aggregate Type
            aggregate_id (str): Aggregate Id

        """
        if aggregate_type not in [PB_TYPE_PREFIX, SBI_TYPE_PREFIX]:
            raise RuntimeError('Invalid aggregate type')
        self._type = aggregate_type
        self._id = aggregate_id
        self._key = self.get_key(aggregate_type, aggregate_id)

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Get the scheduling object ID."""
        return self._id

    @property
    def type(self):
        """Get the scheduling object type."""
        return self._type

    @property
    def key(self):
        """Get the scheduling object key."""
        return self._key

    @property
    def config(self):
        """Get the scheduling object config."""
        return self.get_config()

    @property
    def status(self):
        """Get the status of the object."""
        return self.get_status()

    ###########################################################################
    # PubSub functions
    ###########################################################################

    def subscribe(self, subscriber: str) -> events.EventQueue:
        """Subscribe to Scheduling Block Instance or Processing Block events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return events.subscribe(self._type, subscriber)

    def get_subscribers(self):
        """Get the list of subscribers.

        Get the list of subscribers to Scheduling Block Instance (SBI) or
        Processing Block events.

        Returns:
            List[str], list of subscriber names.

        """
        return events.get_subscribers(self._type)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish a Scheduling Block Instance or Processing Block event.

        Args:
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        events.publish(self._type, self._id,
                       event_type, event_data)

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_status(self) -> str:
        """Get the status of the scheduling data object.

        Returns:
            str, status of sbi or pb.

        """
        # Check that the key exists
        if not DB.get_keys(self._key):
            raise KeyError('Key not found: {}'.format(self._key))

        events_list_key = event_keys.aggregate_events_list(self._key)
        events_data_key = event_keys.aggregate_events_data(self._key)
        last_event = DB.get_hash_value(events_data_key,
                                       DB.get_list_value(events_list_key, -1))
        last_event = ast.literal_eval(last_event)
        return last_event['event_type']

    def get_events(self) -> List[events.Event]:
        """Get events associated with the scheduling data object.

        Get event data for the specified Scheduling block instance or
        processing block.

        Returns:
            list of event data dictionaries

        """
        events_list = []
        event_ids = DB.get_list(event_keys.aggregate_events_list(self._key))
        for event_id in event_ids:
            data = ast.literal_eval(
                DB.get_hash_value(event_keys.aggregate_events_data(self._key),
                                  event_id))
            events_list.append(events.Event(event_id, self._type, '',
                                            data))
        return events_list

    def get_config(self):
        """Get a dictionary representation of the scheduling object data.

        Returns:
            dict

        """
        # Check that the key exists
        if not DB.get_keys(self._key):
            raise KeyError('key not found: {}'.format(self._key))

        config_dict = DB.get_hash_dict(self._key)
        for _, value in config_dict.items():
            for char in ['[', '{']:
                if char in value:
                    value = ast.literal_eval(value)
        return config_dict

    def get_active(self):
        """Get list of active scheduling objects.

        Returns:
            list, list of object/aggregate ids

        """
        return DB.get_list('{}:active'.format(self._type))

    def get_aborted(self):
        """Get list of aborted scheduling objects.

        Returns:
            list, list of object/aggregate ids

        """
        return DB.get_list('{}:aborted'.format(self._type))

    def get_completed(self):
        """Get list of completed scheduling objects.

        Returns:
            list, list of object/aggregate ids

        """
        return DB.get_list('{}:completed'.format(self._type))

    # #########################################################################
    # Utility functions
    # #########################################################################

    @staticmethod
    def get_key(aggregate_type: str, aggregate_id: str):
        """Get a scheduling object key.

        Args:
            aggregate_type (str): Scheduling object type
            aggregate_id (str): Scheduling object id

        Returns:
            str, database key for the scheduling object.

        """
        return '{}:{}'.format(aggregate_type, aggregate_id)

    def _check_exists(self):
        """Raise a KeyError if the scheduling object doesnt exist.

        Raise:
            KeyError, if the object doesnt exist in the database.

        """
        if not DB.get_keys(self._key):
            raise KeyError("Object with key '{}' not exist".format(self._key))
