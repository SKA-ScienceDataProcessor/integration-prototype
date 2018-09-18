# -*- coding: utf-8 -*-
"""High Level Processing Controller Client API."""
import ast
import logging
from typing import List

from . import events
from .event_keys import aggregate_events_data, aggregate_events_list

LOG = logging.getLogger('SIP.EC.CDB')


class ProcessingControllerDbClient:
    """Base class for scheduling block instance and processing block API."""

    def __init__(self, aggregate_type, db):
        """Initialise variables.

        Args:
            aggregate_type (str): Aggregate Type
            db: Configuration Database

        """
        self._aggregate_type = aggregate_type
        self._events = events
        self._db = db

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
        return self._events.subscribe(self._aggregate_type, subscriber)

    def get_subscribers(self):
        """Get the list of subscribers.

        Get the list of subscribers to Scheduling Block Instance (SBI) or
        Processing Block events.

        Returns:
            List[str], list of subscriber names.

        """
        return self._events.get_subscribers(self._aggregate_type)

    def publish(self, block_id: str, event_type: str, event_data: dict = None):
        """Publish a Scheduling Block Instance or Processing Block event.

        Args:
            block_id (str): Scheduling block instance or processing block id.
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        self._events.publish(self._aggregate_type, block_id, event_type,
                             event_data)

    # #########################################################################
    # Get functions
    # #########################################################################

    def get_status(self, block_id: str) -> str:
        """Get the status of an scheduling block instance or processing block.

        Args:
            block_id (str): Scheduling block instance or processing block id.

        Returns:
            str, status of sbi or pb.

        """
        key = self.get_key(block_id)

        # Check that the key exists
        if not self._db.get_keys(key):
            raise KeyError('Block ID not found: {}'.format(block_id))
        key = self.get_event_list_key(block_id)
        last_event = self._db.get_hash_value(self.get_event_data_key(
            block_id), self._db.get_list_value(key, -1))
        last_event = ast.literal_eval(last_event)
        return last_event['type']

    def get_event_list_key(self, block_id: str) -> str:
        """Get event list db key.

        Return the scheduling block instance or processing block events
        list db key.

        Args:
            block_id (str): Scheduling block instance or processing block id

        Returns:
            str, db key for the specified scheduling block instance or
            processing block event data.

        """
        return aggregate_events_list(self.get_key(block_id))

    def get_event_data_key(self, block_id: str) -> str:
        """Get event data db key.

        Return the scheduling block instance or processing block events
        data db key.

        Args:
            block_id (str): Scheduling block instance or processing block id

        Returns:
            str, db key for the specified scheduling block instance or
            processing block event data.

        """
        return aggregate_events_data(self.get_key(block_id))

    def get_events(self, block_id: str) -> List[events.Event]:
        """Get event data.

        Get event data for the specified Scheduling block instance or
        processing block.

        Args:
            block_id (str): Scheduling block instance or processing block id

        Returns:
            list of event data dictionaries

        """
        event_data_key = self.get_event_data_key(block_id)
        event_list = []
        for event_id, data in self._db.get_hash_dict(event_data_key).items():
            data = ast.literal_eval(data)
            event_list.append(events.Event(event_id, self._aggregate_type, '',
                                           data))
        return event_list

    def get_key(self, block_id: str) -> str:
        """Return a Scheduling Block Instance or Processing Block db key.

        Args:
            block_id (str): Scheduling block instance or Processing BLock id

        Returns:
            str, db key for the specified SBI or PB

        """
        return '{}:{}'.format(self._aggregate_type, block_id)

    def get_block_details(self, block_ids: list):
        """Get the details of a Scheduling Block Instance or Processing block.

        Args:
            block_ids (list): List of block IDs

        Returns:
            dict, details of the scheduling block instance or processing block

        """
        # Initialise empty dict
        block_data = {}

        # Convert input to list, if needed
        if not isinstance(block_ids, (list, tuple)):
            block_ids = [block_ids]

        for _id in block_ids:
            sbi_key = self.get_key(_id)

            # Check that the key exists
            if not self._db.get_keys(sbi_key):
                raise KeyError('Scheduling Block Instance not found: {}'
                               .format(_id))

            block_key = self._db.get_keys(sbi_key)[0]
            block_data = self._db.get_hash_dict(block_key)
            # NOTE(BM) unfortunately the following hack doesn't quite work \
            # for keys where the value is a Python object (list, dict etc.) \
            # but is good enough for now where objects are stored as strings.
            for key in block_data:
                for char in ['[', '{']:
                    if char in block_data[key]:
                        block_data[key] = ast.literal_eval(str(
                            block_data[key]))
        return block_data

    def get_active(self):
        """Get list of active blocks.

        Get the list of active scheduling block instance or processing
        block from the database.

        Returns:
            list, Scheduling block instance or processing block ids

        """
        return self._db.get_list('{}:active'.format(self._aggregate_type))

    def get_cancelled(self):
        """Get list of cancelled blocks.

        Get the list of cancelled scheduling block instance or processing
        block from the database.

        Returns:
            list, Scheduling block instance or processing block ids

        """
        return self._db.get_list('{}:cancelled'.format(self._aggregate_type))

    def get_completed(self):
        """Get list of completed blocks.

        Get the list of completed scheduling block instance or processing
        block from the database.

        Returns:
            list, Scheduling block instance or processing block ids

        """
        return self._db.get_list('{}:completed'.format(self._aggregate_type))

    # #########################################################################
    # Update functions
    # #########################################################################

    def update_value(self, block_id: str, field: str, value: str):
        """Update the value of the given block id and field.

        Args:
            block_id (str): Scheduling block instance or processing block id
            field (str): Field of the value that will be updated
            value(str): New value

        """
        self._db.set_hash_value(self.get_key(block_id), field, value)

    # #########################################################################
    # Utility functions
    # #########################################################################

    def clear(self):
        """Clear / drop the entire database.

        Note:
            Use with care!
        """
        self._db.flush_db()
