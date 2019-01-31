# -*- coding: utf-8 -*-
"""Base class for list of scheduling or processing block data objects."""
from typing import List

# from ._scheduling_object import SchedulingObject
from .. import ConfigDb
from .._events.event_queue import EventQueue
from .._events.pubsub import get_subscribers, subscribe

DB = ConfigDb()


class SchedulingObjectList:
    """Base class for SBI and PB data objects API."""

    def __init__(self, object_type: str):
        """Initialise variables.

        Args:
            object_type (str): Object Type

        """
        self.type = object_type

    @property
    def active(self) -> List[str]:
        """Get list of active scheduling objects.

        Returns:
            list, list of object ids

        """
        return DB.get_list('{}:active'.format(self.type))

    @property
    def aborted(self) -> List[str]:
        """Get list of aborted scheduling objects.

        Returns:
            list, list of object ids

        """
        return DB.get_list('{}:aborted'.format(self.type))

    @property
    def completed(self) -> List[str]:
        """Get list of completed scheduling objects.

        Returns:
            list, list of object ids

        """
        return DB.get_list('{}:completed'.format(self.type))

    def subscribe(self, subscriber: str) -> EventQueue:
        """Subscribe to scheduling object events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return subscribe(self.type, subscriber)

    def get_subscribers(self) -> List[str]:
        """Get the list of subscribers.

        Get the list of subscribers to Scheduling Block Instance (SBI) or
        Processing Block events.

        Returns:
            List[str], list of subscriber names.

        """
        return get_subscribers(self.type)

    # def _publish(self, object_id: str, event_type: str,
    #              event_data: dict = None):
    #     """Publish a scheduling object event.
    #
    #     Args:
    #         object_id (str): ID of the scheduling object
    #         event_type (str): Type of event.
    #         event_data (dict, optional): Event data.
    #
    #     """
    #     object_key = SchedulingObject.get_key(self.type, object_id)
    #     publish(event_type=event_type,
    #             event_data=event_data,
    #             object_type=self.type,
    #             object_id=object_id,
    #             object_key=object_key,
    #             origin=None)
