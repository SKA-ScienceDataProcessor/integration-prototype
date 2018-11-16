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
        self._check_exists()

    @staticmethod
    def get_key(aggregate_type: str, aggregate_id: str) -> str:
        """Get a scheduling object key.

        Args:
            aggregate_type (str): Scheduling object type
            aggregate_id (str): Scheduling object id

        Returns:
            str, database key for the scheduling object.

        """
        return '{}:{}'.format(aggregate_type, aggregate_id)

    @property
    def id(self) -> str:
        """Get the scheduling object ID."""
        return self._id

    @property
    def type(self) -> str:
        """Get the scheduling object type."""
        return self._type

    @property
    def key(self) -> str:
        """Get the scheduling object key."""
        return self._key

    @property
    def config(self) -> dict:
        """Get the scheduling object config."""
        # Check that the key exists
        self._check_exists()
        config_dict = DB.get_hash_dict(self._key)
        for _, value in config_dict.items():
            for char in ['[', '{']:
                if char in value:
                    value = ast.literal_eval(value)
        return config_dict

    def get_property(self, property_key: str) -> str:
        """Get a scheduling object property."""
        self._check_exists()
        return DB.get_hash_value(self._key, property_key)

    @property
    def status(self) -> str:
        """Get the status of the scheduling object by querying events.

        Return:
            str, status of the object.

        """
        self._check_exists()
        return DB.get_hash_value(self.key, 'status')

    @status.setter
    def status(self, value):
        """Set the status of the scheduling object."""
        self.set_status(value)

    def set_status(self, value):
        """Set the status of the scheduling object."""
        self._check_exists()
        DB.set_hash_value(self.key, 'status', value)
        self.publish('status_changed', event_data=dict(status=value))

    ###########################################################################
    # Pub/sub events functions
    ###########################################################################

    def subscribe(self, subscriber: str) -> events.EventQueue:
        """Subscribe to scheduling object (SBI or PB).

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return events.subscribe(self._type, subscriber)

    def get_subscribers(self) -> List[str]:
        """Get the list of subscribers..

        Returns:
            List[str], list of subscriber names.

        """
        return events.get_subscribers(self._type)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish a Scheduling Block Instance or Processing Block event.

        Note:
            Ideally publish should not be used directly but by other methods
            which perform actions on the object.

        Args:
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        import inspect
        import os.path
        _stack = inspect.stack()
        _origin = os.path.basename(_stack[3][1]) + '::' + \
            _stack[3][3]+'::L{}'.format(_stack[3][2])
        events.publish(self._type, self._id, event_type, event_data,
                       origin=_origin)

    def get_events(self) -> List[events.Event]:
        """Get events associated with the scheduling object.

        Returns:
            list of Event objects

        """
        event_data_key = event_keys.aggregate_events_data(self._key)
        event_list_key = event_keys.aggregate_events_list(self._key)
        events_list = []
        for event_id in DB.get_list(event_list_key):
            data = DB.get_hash_value(event_data_key, event_id)
            data = ast.literal_eval(data)
            events_list.append(events.Event(event_id, self._type, '', data))
        return events_list

    ###########################################################################
    # Private functions
    ###########################################################################

    def _check_exists(self):
        """Raise a KeyError if the scheduling object doesnt exist.

        Raise:
            KeyError, if the object doesnt exist in the database.

        """
        if not DB.get_keys(self._key):
            raise KeyError("Object with key '{}' not exist".format(self._key))
