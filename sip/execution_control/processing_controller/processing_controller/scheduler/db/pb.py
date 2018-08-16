# coding=utf-8
"""Processing Block (PB) data and events."""
from typing import List

import redis

from . import events

DB = redis.StrictRedis(decode_responses=True)
AGGREGATE_TYPE = 'pb'


def subscribe(subscriber: str) -> events.EventQueue:
    """Subscribe to Processing Block (PB) events.

    Args:
        subscriber (str): Subscriber name.

    Returns:
        events.EventQueue, Event queue object for querying PB events.

    """
    return events.subscribe(AGGREGATE_TYPE, subscriber)


def get_subscribers() -> List[str]:
    """Get the list of subscribers to Processing Block (PB) events.

    Returns:
        List[str], list of subscriber names.

    """
    return events.get_subscribers(AGGREGATE_TYPE)


def publish(pb_key: str, event_type: str, event_data: dict = None):
    """Publish a PB event.

    Args:
        pb_key (str): Key of the SBI.
        event_type (str): Type of event.
        event_data (dict, optional): Event data.

    """
    events.publish(AGGREGATE_TYPE, pb_key, event_type, event_data)
