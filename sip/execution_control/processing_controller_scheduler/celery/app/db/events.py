# coding=utf-8
"""Execution Control Configuration database events module.

An aggregate is a domain-driven-design (DDD) concept.
You apply a command to an aggregate which then produces one or more events.

For SIP the aggregates are the:

    - Processing Block
    - Scheduling Block Instance

Events are created when a new Processing Block or Scheduling Block Instance
is created, cancelled etc.

A higher level events API is also provided in the modules `pb_events.py` and
`sbi_events.py`.

"""
from typing import List
import ast
import redis

from . import event_keys as keys


# TODO(BM) Replace redis db client object with low level API object.
DB = redis.StrictRedis(decode_responses=True)


class Event:
    """Event class."""

    def __init__(self, event_id, aggregate_type, subscriber, event_data):
        """Initialise the event."""
        self.aggregate_type = aggregate_type
        self.subscriber = subscriber
        self.id = event_id
        self.data = event_data

    def __str__(self):
        """Used to generate the 'informal' string representation.

         Used by the print statement.
         """
        return str(dict(id=self.id, data=self.data))

    def __repr__(self):
        """Generates the 'official' string representation.

        eg. used when printing lists of objects.
        """
        return 'events:{}:{}:{}'.format(self.aggregate_type,
                                        self.subscriber, self.id)

    def complete(self):
        """Retire event from the active to history.

        This should be called when processing of the event by the handler is
        complete.
        """
        pipe = DB.pipeline()
        pipe.lrem(keys.active(self.aggregate_type, self.subscriber), 0,
                  self.id)
        pipe.rpush(keys.history(self.aggregate_type, self.subscriber),
                   self.id)
        pipe.execute()


class EventQueue:
    """Event queue class.

     Used to poll for subscribed events and query the list of published
     and active events for a given aggregate type and subscriber.
     """

    def __init__(self, aggregate_type: str, subscriber: str):
        """Initialise the event queue.

        Subscribes to Redis pub/sub events of the given aggregate type.

        Args:
            aggregate_type (str): Aggregate type
            subscriber (str): Subscriber name

        """
        self._queue = DB.pubsub()
        self._queue.subscribe(aggregate_type)
        self._pub_key = keys.published(aggregate_type, subscriber)
        self._data_key = keys.data(aggregate_type, subscriber)
        self._active_key = keys.active(aggregate_type, subscriber)
        self._aggregate_type = aggregate_type
        self._subscriber = subscriber

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

    def get_published_events(self) -> List[Event]:
        """Get all published events.

        Any event return by this method is made active (ie. removed from the
        published events list and moved to the active events list).

        This method is intended to be used to recover events missed by
        the get() method which might be needed if recovering when a subscriber
        goes down. Events returned are moved to the active list with a
        single atomic transaction.

        Return:
            list[Events], list of Event objects

        """
        pipe = DB.pipeline()
        pipe.watch(self._pub_key)
        event_ids = pipe.lrange(self._pub_key, 0, -1)
        if event_ids:
            pipe.delete(self._pub_key)
            pipe.lpush(self._active_key, *event_ids)
        pipe.execute()
        events = []
        for event_id in event_ids:
            event_data = ast.literal_eval(DB.hget(self._data_key, event_id))
            events.append(Event(event_id, self._aggregate_type,
                                self._subscriber, event_data))
        return events

    def get_active_events(self) -> List[Event]:
        """Get all active events.

        This method is intended to be used to recover events stuck in the
        active state which could happen if an event handling processing
        an active event goes down before completing the event processing.

        Returns:
            list[Events], list of event objects.

        """
        event_ids = DB.lrange(self._active_key, 0, -1)
        events = []
        for event_id in event_ids:
            event_data = ast.literal_eval(DB.hget(self._data_key, event_id))
            events.append(Event(event_id, self._aggregate_type,
                                self._subscriber, event_data))
        return events

    def _get_event(self) -> Event:
        """Retrieve an event.

        Private method, used to return an active Event object to a subscriber
        after it has received an event notification.

        Returns:
            Event, (Active) event object
        """
        event_id = DB.rpoplpush(src=self._pub_key, dst=self._active_key)
        event_data = ast.literal_eval(DB.hget(self._data_key, event_id))
        return Event(event_id, self._aggregate_type, self._subscriber,
                     event_data)


def subscribe(aggregate_type: str, subscriber: str) -> EventQueue:
    """Subscribe to the specified aggregate type.

    Returns an event queue object which can be used to query events
    associated with the aggregate type for this subscriber.

    Args:
        aggregate_type (str): Aggregate type
        subscriber (str): Subscriber name

    Returns:
        EventQueue, event queue object.

    """
    key = keys.subscribers(aggregate_type)
    DB.lrem(key, 0, subscriber)
    DB.lpush(key, subscriber)
    return EventQueue(aggregate_type, subscriber)


def get_subscribers(aggregate_type: str) -> List[str]:
    """Get the list of subscribers to events from the aggregate type.

    Args:
        aggregate_type (str): Type of aggregate.

    Returns:
        List[str], list of subscriber names.

    """
    return DB.lrange(keys.subscribers(aggregate_type), 0, -1)


def publish(aggregate_type: str, aggregate_key: str, event_type: str,
            event_data: dict = None):
    """Publish an event.

    Writes the event id and event data to all subscribers as well as to the
    event store of the aggregate.

    Args:
        aggregate_type (str): Type of aggregate
        aggregate_key (str): db key for the aggregate
        event_type (str): The event type
        event_data (dict, optional): Optional event data

    """
    # TODO(BM) check if the aggregate key is in the db?!

    # Create a pipeline object that queues multiple commands as a single
    # atomic transaction
    pipe = DB.pipeline()

    # Get a unique event key
    # FIXME(BM) there is a risk here that the event id and publishing the \
    # event is not an atomic operation.
    event_id = _get_event_id(aggregate_type)

    # Add the aggregate 'id' and 'type' if not already in the event data.
    if event_data is None:
        event_data = dict()
    aggregate_id_key = '{}_id'.format(aggregate_type)
    if aggregate_id_key not in event_data:
        event_data[aggregate_id_key] = aggregate_key
    if 'type' not in event_data:
        event_data['type'] = event_type

    # Publish the event to subscribers
    _publish_to_subscribers(pipe, aggregate_type, event_id, event_data)

    # Update the aggregate event list and data.
    _update_aggregate(pipe, aggregate_key, event_id, event_data)

    # Execute the set of db transactions as an atomic transaction.
    pipe.execute()


def _publish_to_subscribers(pipe: redis.client.StrictPipeline,
                            aggregate_type: str, event_id: str,
                            event_data: dict):
    """Publish and event to all subscribers.

    - Adds the event id to the published event list for all subscribers.
    - Adds the event data to the published event data for all subscribers.
    - Publishes the event id notification to all subscribers.

    Args:
        pipe: Redis transaction pipeline object.
        aggregate_type (str): Type of aggregate.
        event_id (str): Event ID.
        event_data (dict): Event data.

    """
    # Get list of subscribers
    subscribers = get_subscribers(aggregate_type)

    # Add the event to each subscribers published list
    for sub in subscribers:
        pipe.lpush(keys.published(aggregate_type, sub), event_id)
        pipe.hset(keys.data(aggregate_type, sub), event_id,
                  event_data)
    pipe.publish(aggregate_type, event_id)


def _update_aggregate(pipe: redis.client.StrictPipeline, aggregate_key: str,
                      event_id: str, event_data: dict):
    """Update the aggregate's events list and events data.

    - Adds the event Id to the list of events for the aggregate.
    - Adds the event data to the hash of aggregate event data keyed by event id.

    Args:
        pipe (redis.client.StrictPipeline): Redis transaction group object.
        aggregate_key (str): Key of the aggregate being updated.
        event_id (str): Event id
        event_data (dict): Event data dictionary.

    """
    pipe.lpush(keys.aggregate_events_list(aggregate_key), event_id)
    pipe.hset(keys.aggregate_events_data(aggregate_key), event_id, event_data)


def _get_event_id(aggregate_type: str) -> str:
    """Return an event key for the event on the aggregate type.

    This must be a unique event id for the aggregate.

    Args:
        aggregate_type (str): Type of aggregate

    Returns:
        str, event id

    """
    key = keys.event_counter(aggregate_type)
    pipe = DB.pipeline()
    pipe.watch(key)
    count = DB.get(key)
    DB.incr(key)
    pipe.execute()
    if count is None:
        count = 0
    return '{}_event_{:08d}'.format(aggregate_type, int(count))


