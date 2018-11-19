# -*- coding: utf-8 -*-
"""Base class for scheduling or processing block data objects."""
import ast
from typing import List

from ._keys import PB_KEY, SBI_KEY
from .. import DB, LOG, _events


class SchedulingObject:
    """Base class for SBI and PB data objects API."""

    def __init__(self, object_type: str, object_id: str = None):
        """Initialise variables.

        Args:
            object_type (str): Type of object.
            object_id (str): ID of the object.

        """
        if object_type not in [PB_KEY, SBI_KEY]:
            raise RuntimeError('Invalid object type')
        self._type = object_type
        self._id = object_id
        self._key = self.get_key(object_type, object_id)
        self._check_object_exists()

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
        self._check_object_exists()
        config_dict = DB.get_hash_dict(self.key)
        for _, value in config_dict.items():
            for char in ['[', '{']:
                if char in value:
                    value = ast.literal_eval(value)
        return config_dict

    def get_property(self, property_key: str) -> str:
        """Get a scheduling object property."""
        self._check_object_exists()
        return DB.get_hash_value(self.key, property_key)

    @property
    def status(self) -> str:
        """Get the status of the scheduling object by querying events.

        Return:
            str, status of the object.

        """
        self._check_object_exists()
        return DB.get_hash_value(self.key, 'status')

    @status.setter
    def status(self, value):
        """Set the status of the scheduling object."""
        self.set_status(value)

    def set_status(self, value):
        """Set the status of the scheduling object."""
        self._check_object_exists()
        DB.set_hash_value(self.key, 'status', value)
        self.publish('status_changed', event_data=dict(status=value))

    @staticmethod
    def get_key(object_type: str, object_id: str):
        """Return the database key scheduling object of specified type & id."""
        return '{}:{}'.format(object_type, object_id)

    ###########################################################################
    # Pub/sub events functions
    ###########################################################################

    def subscribe(self, subscriber: str) -> _events.EventQueue:
        """Subscribe to scheduling object (SBI or PB).

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return _events.subscribe(self._type, subscriber)

    def get_subscribers(self) -> List[str]:
        """Get the list of subscribers to the scheduling object.

        Returns:
            List[str], list of subscriber names.

        """
        return _events.get_subscribers(self._type)

    def publish(self, event_type: str, event_data: dict = None):
        """Publish an event associated with the scheduling object.

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

        _events.publish(event_type=event_type,
                        event_data=event_data,
                        object_type=self._type,
                        object_id=self._id,
                        object_key=self._key,
                        origin=_origin)

    def get_events(self) -> List[_events.Event]:
        """Get events associated with the scheduling object.

        Returns:
            list of Event objects

        """
        LOG.debug('Getting events for %s', self.key)
        return _events.get_events(self.key)

    def get_event_queue(self, subscriber: str):
        """Get an event queue for the specified subscriber."""
        return _events.EventQueue(self._type, subscriber)

    ###########################################################################
    # Private functions
    ###########################################################################

    def _check_object_exists(self):
        """Raise a KeyError if the scheduling object doesnt exist.

        Raise:
            KeyError, if the object doesnt exist in the database.

        """
        if not DB.get_keys(self.key):
            raise KeyError("Object with key '{}' not exist".format(self.key))
