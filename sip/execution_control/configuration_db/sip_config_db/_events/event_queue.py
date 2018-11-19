# coding=utf-8
"""SIP EC config database event queue class."""
import ast
from typing import Callable, List, Union

from . import Event, _keys
from .. import DB, LOG


class EventQueue:
    """Event queue class.

    Used to poll for subscribed events and query the list of published
    and processed events for a given object type and subscriber.
    """

    def __init__(self, object_type: str, subscriber: str,
                 callback_handler: Callable = None):
        """Initialise the event queue.

        Subscribes to Redis pub/sub events of the given object type.

        Args:
            object_type (str): Object type
            subscriber (str): Subscriber name

        """
        self._queue = DB.pub_sub()
        if callback_handler is None:
            self._queue.subscribe(object_type)
        else:
            self._queue.subscribe(**{object_type: callback_handler})
        self._pub_key = _keys.published(object_type, subscriber)
        self._data_key = _keys.data(object_type, subscriber)
        self._processed_key = _keys.processed_events(object_type, subscriber)
        self._object_type = object_type
        self._subscriber = subscriber

    def pubsub(self):
        """Return the Redis pubsub object."""
        return self._queue

    def get(self) -> Union[Event, None]:
        """Get the latest event from the queue.

        Call this method to query the queue for the latest event.

        If no event has been published None is returned.

        Returns:
              Event or None

        """
        message = self._queue.get_message()
        if message and message['type'] == 'message':
            event_id = DB.get_event(self._pub_key, self._processed_key)
            event_data_str = DB.get_hash_value(self._data_key, event_id)
            event_dict = ast.literal_eval(event_data_str)
            event_dict['id'] = event_id
            event_dict['subscriber'] = self._subscriber
            return Event.from_config(event_dict)
        return None

    def get_published_events(self, process=True) -> List[Event]:
        """Get a list of published (pending) events.

        Return a list of Event objects which have been published
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
        LOG.debug('Getting published events (%s)', self._pub_key)
        if process:
            LOG.debug('Marking returned published events as processed.')
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
            event_str = DB.get_hash_value(self._data_key, event_id)
            event_dict = ast.literal_eval(event_str)
            event_dict['id'] = event_id
            event = Event.from_config(event_dict)
            LOG.debug('Loaded event: %s (%s)', event.id, event.type)
            events.append(event)
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
            event_str = DB.get_hash_value(self._data_key, event_id)
            event_dict = ast.literal_eval(event_str)
            event_dict['id'] = event_id
            event_dict['subscriber'] = self._subscriber
            events.append(Event.from_config(event_dict))
        return events

    def complete_event(self, event_id: str):
        """Complete the specified event."""
        event_ids = DB.get_list(self._processed_key)
        if event_id not in event_ids:
            raise KeyError('Unable to complete event. Event {} has not been '
                           'processed (ie. it is not in the processed '
                           'list).'.format(event_id))
        DB.remove_from_list(self._processed_key, event_id, pipeline=True)
        key = _keys.completed_events(self._object_type, self._subscriber)
        DB.append_to_list(key, event_id, pipeline=True)
        DB.execute()
