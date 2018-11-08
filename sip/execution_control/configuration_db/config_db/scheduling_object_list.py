# -*- coding: utf-8 -*-
"""Base class for list of scheduling or processing block data objects."""
import logging
from typing import List

from . import events
from .config_db_redis import ConfigDb

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()


class SchedulingObjectList:
    """Base class for SBI and PB data objects API."""

    def __init__(self, aggregate_type: str):
        """Initialise variables.

        Args:
            aggregate_type (str): Aggregate Type

        """
        self.type = aggregate_type

    @property
    def num_active(self) -> int:
        """Get the number of active scheduling objects."""
        return len(self.active)

    @property
    def num_aborted(self) -> int:
        """Get the number of aborted scheduling objects."""
        return len(self.aborted)

    @property
    def num_completed(self) -> int:
        """Get the number of completed scheduling objects."""
        return len(self.completed)

    @property
    def active(self) -> List[str]:
        """Get list of active scheduling objects.

        Returns:
            list, list of object/aggregate ids

        """
        return DB.get_list('{}:active'.format(self.type))

    @property
    def aborted(self) -> List[str]:
        """Get list of aborted scheduling objects.

        Returns:
            list, list of object/aggregate ids

        """
        return DB.get_list('{}:aborted'.format(self.type))

    @property
    def completed(self) -> List[str]:
        """Get list of completed scheduling objects.

        Returns:
            list, list of object/aggregate ids

        """
        return DB.get_list('{}:completed'.format(self.type))

    ###########################################################################
    # Pub/sub events functions
    ###########################################################################

    def subscribe(self, subscriber: str) -> events.EventQueue:
        """Subscribe to scheduling object events.

        Args:
            subscriber (str): Subscriber name.

        Returns:
            events.EventQueue, Event queue object for querying PB events.

        """
        return events.subscribe(self.type, subscriber)

    def get_subscribers(self) -> List[str]:
        """Get the list of subscribers.

        Get the list of subscribers to Scheduling Block Instance (SBI) or
        Processing Block events.

        Returns:
            List[str], list of subscriber names.

        """
        return events.get_subscribers(self.type)

    def publish(self, object_id: str, event_type: str,
                event_data: dict = None):
        """Publish a scheduling object event.

        Args:
            object_id (str): ID of the scheduling object
            event_type (str): Type of event.
            event_data (dict, optional): Event data.

        """
        events.publish(self.type, object_id, event_type, event_data)
