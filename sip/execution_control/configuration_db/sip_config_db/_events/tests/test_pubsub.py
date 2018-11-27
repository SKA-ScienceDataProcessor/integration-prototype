# coding=utf-8
"""Test of the Configuration Database events interface."""
import time
from threading import Thread

from ..event_queue import EventQueue
from ..pubsub import get_subscribers, publish, subscribe
from ... import ConfigDb

DB = ConfigDb()


def test_events_subscribe():
    """Test subscribing to events."""
    DB.flush_db()
    object_type = 'test_object'
    subscriber = 'test_subscriber'
    subscribe(object_type, subscriber)
    assert subscriber in get_subscribers(object_type)


def test_events_basic_usage():
    """Misc tests of the events interface."""
    DB.flush_db()

    event_type = 'test_event_type'
    subscriber = 'test_subscriber'
    object_type = 'test_object'
    object_id = 'test_object_id'

    # Subscribe to 'test' events with the 'test' subscriber
    event_queue = subscribe(object_type, subscriber)
    assert subscriber in get_subscribers(object_type)

    # Publish an event.
    publish(event_type, object_type=object_type, object_id=object_id)

    # Keep asking for events until we get one.
    while True:
        event = event_queue.get()
        if event:
            assert event.id == '{}_event_00000000'.format(object_type)
            assert event.type == event_type
            assert not event.data
            assert not event.origin
            assert event.timestamp
            assert event.object_id == object_id
            assert event.object_type == object_type
            assert not event.object_key
            break

    # There should be no published events as we already got the
    # only event.
    assert not event_queue.get_published_events()

    # There should be one active event.
    active_events = event_queue.get_processed_events()
    assert len(active_events) == 1
    assert active_events[0].id == '{}_event_00000000'.format(object_type)


# Global counter to verify the callback function was triggered the correct
# number of times.
CALLBACK_EVENT_COUNT = 0


def test_events_with_callback():
    """Test subscribing to events with a callback handler."""
    def _callback_handler(message):
        """Event callback handler."""
        global CALLBACK_EVENT_COUNT  # pylint: disable=global-statement
        CALLBACK_EVENT_COUNT += 1
        assert 'callback_test_event_' in message['data']
        # print('EVENT CALLBACK!! ', message['data'], CALLBACK_EVENT_COUNT)

    def _watcher_function(queue: EventQueue, timeout: float):
        """Monitor for events."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            queue.get()
            time.sleep(0.1)

    DB.flush_db()
    object_type = 'callback_test'
    subscriber = 'test_subscriber'
    event_type = 'test'
    object_id = 'test-01'

    # Subscribe to the 'pb' object events with the 'test' subscriber
    event_queue = subscribe(object_type, subscriber,
                            _callback_handler)
    assert subscriber in get_subscribers(object_type)

    # Test using a custom watcher thread for the event loop.
    thread = Thread(target=_watcher_function, args=(event_queue, 2.0,),
                    daemon=False)
    thread.start()
    for _ in range(10):
        publish(event_type=event_type, object_type=object_type,
                object_id=object_id)
    thread.join()
    assert CALLBACK_EVENT_COUNT == 10

    # Test using the provided pubsub subscriber thread
    thread = event_queue.pubsub().run_in_thread(sleep_time=0.01)
    for _ in range(10):
        publish(event_type=event_type, object_type=object_type,
                object_id=object_id)
    time.sleep(0.5)
    thread.stop()
    assert CALLBACK_EVENT_COUNT == 20


def test_events_recovery():
    """Test event recovery, eg. after a subscriber service crash."""
    DB.flush_db()
    event_type = 'test_event'
    subscriber = 'test_subscriber'
    object_type = 'test_object_type'
    object_id = 'test_object_id'

    # Start a subscriber that goes away. eg it crashes, or in this case is a
    # temp thread that finishes after subscribing.
    temp_subscriber = Thread(target=subscribe, args=[object_type, subscriber])
    temp_subscriber.start()
    temp_subscriber.join()

    # While the subscriber is not getting events (it is a temp thread
    # that has finished), some events are published.
    publish(event_type, object_type=object_type, object_id=object_id,
            event_data={'counter': 1})
    publish(event_type, object_type=object_type, object_id=object_id,
            event_data={'counter': 2})

    # When the subscriber comes back, it will resubscribe but calling
    # get on the event queue will not return any events as event notifications
    # were missed.
    event_queue = subscribe(object_type, subscriber)
    event_count = 0
    for _ in range(100):
        event = event_queue.get()
        if event:
            event_count += 1
    assert event_count == 0

    # At this point, since we cleared the db for the test, there are no
    # active (previously acknowledged) events
    active_events = event_queue.get_processed_events()
    assert not active_events

    # Get published events without processing them (ie. process == False)
    # (Events returned with process=False will not be marked as processed.
    published_events = event_queue.get_published_events(process=False)
    assert len(published_events) == 2

    # Get published events again, this time mark as processed..
    published_events = event_queue.get_published_events()
    assert len(published_events) == 2

    # Get published events yet again, this time there should be none as
    # they have been 'processed'.
    published_events = event_queue.get_published_events()
    assert not published_events

    # After asking for published events they are moved to the active queue.
    active_events = event_queue.get_processed_events()
    assert len(active_events) == 2

    # If we complete the active events.
    for event in active_events:
        event_queue.complete_event(event.id)

    # They are moved to the history queue and are no longer active.
    active_events = event_queue.get_processed_events()
    assert not active_events
