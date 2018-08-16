# coding=utf-8
"""Test the processing block events API."""
from random import choice

from ..scheduler.db.pb import subscribe, publish


def test_pb_events():
    """Test the PB events API"""
    subscriber = 'pb_events_test'
    event_queue = subscribe(subscriber)
    event_count = 4

    pb_key = 'pb:{:03d}'.format(0)
    publish(pb_key, 'created')
    for _ in range(event_count):
        event_type = choice(['cancelled', 'queued', 'scheduled'])
        publish(pb_key, event_type)

    events = []
    while len(events) != 5:
        event = event_queue.get()
        if event:
            assert event.id == 'pb_event_{:08d}'.format(len(events))
            assert event.data['pb_id'] == 'pb:000'
            events.append(event)

    # print(events[0])

    # TODO(BM) check the status of the aggregate after the event has been \
    # applied
