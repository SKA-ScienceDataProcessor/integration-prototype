# coding=utf-8
"""Execution Control Configuration database events module.

An aggregate is a domain-driven-design (DDD) concept.
You apply a command to an aggregate which then produces one or more events.
"""
import ast
import datetime
from typing import Callable, List

from . import event_keys as keys
from .config_db_redis import ConfigDb

DB = ConfigDb()


class Event:
    """Event class."""

    def __init__(self, event_id, aggregate_type, subscriber, event_data):
        """Initialise the event."""
        self.aggregate_type = aggregate_type
        self.subscriber = subscriber
        self._id = event_id
        self._data = event_data

    def __str__(self):
        """Generate the 'informal' string representation.

        Used by the print statement.
        """
        return str(dict(id=self._id, data=self._data))

    def __repr__(self):
        """Generate the 'official' string representation.

        eg. used when printing lists of objects.
        """
        return '{}'.format(self._id)

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Return the event id."""
        return self._id

    @property
    def type(self):
        """Return the type of event."""
        return self._data['event_type']

    @property
    def data(self):
        """Return the event data."""
        return self._data['event_data']

    @property
    def object_type(self):
        """Return the aggregate/object type associated with the event."""
        return self._data['object_type']

    @property
    def object_id(self):
        """Return the aggregate/object id associated with the event."""
        return self._data['object_id']

    def complete(self):
        """Retire event from the processed list to history.

        This should be called when processing of the event by the handler is
        complete.
        """
        key = keys.processed(self.aggregate_type, self.subscriber)
        DB.remove_from_list(key, self._id)


class EventQueue:
    """Event queue class.

    Used to poll for subscribed events and query the list of published
    and processed events for a given aggregate type and subscriber.
    """

    def __init__(self, aggregate_type: str, subscriber: str,
                 callback_handler: Callable = None):
        """Initialise the event queue.

        Subscribes to Redis pub/sub events of the given aggregate type.

        Args:
            aggregate_type (str): Aggregate type
            subscriber (str): Subscriber name

        """
        self._queue = DB.pub_sub()
        if callback_handler is None:
            self._queue.subscribe(aggregate_type)
        else:
            self._queue.subscribe(**{aggregate_type: callback_handler})
        self._pub_key = keys.published(aggregate_type, subscriber)
        self._data_key = keys.data(aggregate_type, subscriber)
        self._processed_key = keys.processed(aggregate_type, subscriber)
        self._aggregate_type = aggregate_type
        self._subscriber = subscriber

    def pubsub(self):
        """Return the Redis pubsub object."""
        return self._queue

    def get(self):
        """Get the latest event from the queue.

        Call this method to query the queue for the latest event.

        If no event has been published None is returned.

        Returns:
              Event or None

        """
        message = self._queue.get_message()
        if message and message['type'] == 'message':
            return self._get_event()
        return None

    def get_published_events(self, process=True) -> List[Event]:
        """Get a list of published (pending) events.

        Return a list of event.Event objects which have been published
        and are therefore pending to be processed. If the process argument
        is set to true, any events returned from this method will also be
        marked as processed by moving them to the processed events queue.

        This method is intended to be used either to print the list of
        pending published events, or also to recover from events
        missed by the get() method. The latter of these use cases may be needed
        for recovering when a subscriber drops out.

        Args:
            process (bool): If true, also move the events to the Processed
                            event queue.

        Return:
            list[Events], list of Event objects

        """
        if process:
            DB.watch(self._pub_key, pipeline=True)
            event_ids = DB.get_list(self._pub_key, pipeline=True)
            if event_ids:
                DB.delete(self._pub_key, pipeline=True)
                DB.append_to_list(self._processed_key, *event_ids,
                                  pipeline=True)
            DB.execute()
        else:
            event_ids = DB.get_list(self._pub_key)

        events = []
        for event_id in event_ids[::-1]:
            event_data = ast.literal_eval(DB.get_hash_value(self._data_key,
                                                            event_id))
            events.append(Event(event_id, self._aggregate_type,
                                self._subscriber, event_data))
        return events

    def get_processed_events(self) -> List[Event]:
        """Get all processed events.

        This method is intended to be used to recover events stuck in the
        processed state which could happen if an event handling processing
        an processed event goes down before completing the event processing.

        Returns:
            list[Events], list of event objects.

        """
        event_ids = DB.get_list(self._processed_key)
        events = []
        for event_id in event_ids:
            event_data = ast.literal_eval(DB.get_hash_value(self._data_key,
                                                            event_id))
            events.append(Event(event_id, self._aggregate_type,
                                self._subscriber, event_data))
        return events

    def _get_event(self) -> Event:
        """Retrieve an event.

        Private method, used to return an processed Event object to a
        subscriber after it has received an event notification.

        Returns:
            Event, (processed) event object

        """
        event_id = DB.get_event(self._pub_key, self._processed_key)
        event_data = ast.literal_eval(DB.get_hash_value(self._data_key,
                                                        event_id))
        return Event(event_id, self._aggregate_type, self._subscriber,
                     event_data)


def subscribe(aggregate_type: str, subscriber: str,
              callback_handler: Callable = None) -> EventQueue:
    """Subscribe to the specified aggregate type.

    Returns an event queue object which can be used to query events
    associated with the aggregate type for this subscriber.

    Args:
        aggregate_type (str): Aggregate type
        subscriber (str): Subscriber name
        callback_handler (function, optional): Callback handler function.

    Returns:
        EventQueue, event queue object.

    """
    key = keys.subscribers(aggregate_type)
    DB.remove_from_list(key, subscriber)
    DB.append_to_list(key, subscriber)
    return EventQueue(aggregate_type, subscriber, callback_handler)


def get_subscribers(aggregate_type: str) -> List[str]:
    """Get the list of subscribers to events from the aggregate type.

    Args:
        aggregate_type (str): Type of aggregate.

    Returns:
        List[str], list of subscriber names.

    """
    return DB.get_list(keys.subscribers(aggregate_type))


def publish(aggregate_type: str, aggregate_id: str, event_type: str,
            event_data: dict = None, origin: str = None):
    """Publish an event.

    Writes the event id and event data to all subscribers as well as to the
    event store of the aggregate.

    Args:
        aggregate_type (str): Type of aggregate
        aggregate_id (str): Aggregate ID
        event_type (str): The event type
        event_data (dict, optional): Optional event data
        origin (str): Origin or publisher of the event.

    """
    # Get a unique event key
    # event is not an atomic operation.
    event_id = _get_event_id(aggregate_type)

    # Add the aggregate 'id' and 'type' if not already in the event data.
    event_dict = dict(timestamp=datetime.datetime.utcnow().isoformat())
    if 'object_type' not in event_dict:
        event_dict['object_type'] = aggregate_type
    if 'object_id' not in event_dict:
        event_dict['object_id'] = aggregate_id
    if 'event_type' not in event_dict:
        event_dict['event_type'] = event_type
    if event_data is not None:
        event_dict['event_data'] = event_data
    if origin is not None and 'origin' not in event_dict:
        event_dict['origin'] = origin

    # Publish the event to subscribers
    _publish_to_subscribers(aggregate_type, event_id, event_dict)

    # Update the aggregate event list and data.
    aggregate_key = '{}:{}'.format(aggregate_type, aggregate_id)
    _update_aggregate(aggregate_key, event_id, event_dict)

    # Execute the set of db transactions as an atomic transaction.
    DB.execute()


def _publish_to_subscribers(aggregate_type: str, event_id: str,
                            event_data: dict):
    """Publish and event to all subscribers.

    - Adds the event id to the published event list for all subscribers.
    - Adds the event data to the published event data for all subscribers.
    - Publishes the event id notification to all subscribers.

    Args:
        aggregate_type (str): Type of aggregate.
        event_id (str): Event ID.
        event_data (dict): Event data.

    """
    # Get list of subscribers
    subscribers = get_subscribers(aggregate_type)

    # Add the event to each subscribers published list
    for sub in subscribers:
        DB.prepend_to_list(keys.published(aggregate_type, sub), event_id,
                           pipeline=True)
        DB.set_hash_value(keys.data(aggregate_type, sub), event_id,
                          event_data, pipeline=True)
    DB.publish(aggregate_type, event_id, pipeline=True)


def _update_aggregate(aggregate_key: str, event_id: str, event_data: dict):
    """Update the events list and events data for the aggregate.

    - Adds the event Id to the list of events for the aggregate.
    - Adds the event data to the hash of aggregate event data keyed by event
      id.

    Args:
        aggregate_key (str): Key of the aggregate being updated.
        event_id (str): Event id
        event_data (dict): Event data dictionary.

    """
    events_list_key = keys.aggregate_events_list(aggregate_key)
    events_data_key = keys.aggregate_events_data(aggregate_key)
    DB.append_to_list(events_list_key, event_id, pipeline=True)
    DB.set_hash_value(events_data_key, event_id, event_data, pipeline=True)


def _get_event_id(aggregate_type: str) -> str:
    """Return an event key for the event on the aggregate type.

    This must be a unique event id for the aggregate.

    Args:
        aggregate_type (str): Type of aggregate

    Returns:
        str, event id

    """
    key = keys.event_counter(aggregate_type)
    DB.watch(key, pipeline=True)
    count = DB.get_value(key)
    DB.increment(key)
    DB.execute()
    if count is None:
        count = 0
    return '{}_event_{:08d}'.format(aggregate_type, int(count))
