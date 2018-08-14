# coding=utf-8
"""Scheduling Block Instance (SBI) Events."""
from typing import List

from . import events

AGGREGATE_TYPE = 'sbi'


def subscribe(subscriber: str) -> events.EventQueue:
    """Subscribe to Scheduling Block Instance (SBI) events.

    Args:
        subscriber (str): Subscriber name.

    Returns:
        events.EventQueue, Event queue object for querying PB events.

    """
    return events.subscribe(AGGREGATE_TYPE, subscriber)


def get_subscribers() -> List[str]:
    """Get the list of subscribers to Scheduling Block Instance (SBI) events.


    Returns:
        List[str], list of subscriber names.

    """
    return events.get_subscribers(AGGREGATE_TYPE)


def publish(sbi_key: str, event_type: str, event_data: dict = None):
    """Publish a SBI event.

    Args:
        sbi_key (str): Key of the SBI.
        event_type (str): Type of event.
        event_data (dict, optional): Event data.

    """
    events.publish(AGGREGATE_TYPE, sbi_key, event_type, event_data)
