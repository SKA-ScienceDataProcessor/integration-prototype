# coding=utf-8
"""Processing Block Events module."""
from datetime import datetime

from . import events


EVENT_TYPE = 'processing_block'


def subscribe(subscriber: str) -> events.EventQueue:
    """Create a subscriber for Processing Block events.

    Args:
        subscriber (str): Name or type of subscriber (eg. the service name).

    Returns:
        Processing Block event queue

    """
    return events.subscribe(EVENT_TYPE, subscriber)


def get_subscribers() -> list:
    """Return list of subscribers of Processing Block events.

    Returns:
        list, names of current subscribers to Processing Block events

    """
    return events.get_subscribers(EVENT_TYPE)


def unsubscribe(subscriber: str):
    """Remove specified subscriber from Processing Block events.

    Args:
        subscriber (str): Name or type of subscriber to remove

    """
    events.unsubscribe(EVENT_TYPE, subscriber)


def publish_new_processing_block_event(block_id: str):
    """Publish an Event notifying subscribers of a new Processing Block.

    Arg:
        block_id (str): The ID of the Processing Block.

    """
    data = dict(type="new", id=block_id, date=datetime.utcnow())
    events.publish(EVENT_TYPE, data=data)


def publish_cancel_processing_block_event(block_id):
    """Publish an Event notifying subscribers of a cancelled Processing Block.

    Arg:
        block_id (str): The ID of the Processing Block.

    """
    data = dict(type="cancel", id=block_id, date=datetime.utcnow())
    events.publish(EVENT_TYPE, data=data)
